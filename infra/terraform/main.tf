locals {
  name_prefix = "pulsewire-${var.environment}"
  common_labels = merge({
    app         = "pulsewire"
    environment = var.environment
    managed_by  = "terraform"
  }, var.labels)

  backend_default_env = {
    APP_ENV         = var.environment
    REDIS_URL       = "redis://${module.memorystore.host}:${module.memorystore.port}/0"
    FRONTEND_ORIGIN = module.frontend_service.url
  }
}

resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com"
  ])

  service            = each.value
  disable_on_destroy = false
}

module "artifact_registry" {
  source      = "./modules/artifact_registry"
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  labels      = local.common_labels

  depends_on = [google_project_service.required]
}

module "networking" {
  source             = "./modules/networking"
  project_id         = var.project_id
  region             = var.region
  environment        = var.environment
  network_name       = var.vpc_name
  subnet_name        = var.subnet_name
  subnet_cidr        = var.subnet_cidr
  connector_name     = var.vpc_connector_name
  connector_cidr     = var.vpc_connector_cidr
  labels             = local.common_labels

  depends_on = [google_project_service.required]
}

module "service_accounts" {
  source      = "./modules/service_accounts"
  project_id  = var.project_id
  environment = var.environment

  depends_on = [google_project_service.required]
}

module "secret_manager" {
  source      = "./modules/secret_manager"
  project_id  = var.project_id
  secrets     = var.secrets
  labels      = local.common_labels
  environment = var.environment

  depends_on = [google_project_service.required]
}

module "cloud_sql" {
  source                = "./modules/cloud_sql"
  project_id            = var.project_id
  region                = var.region
  environment           = var.environment
  db_name               = var.db_name
  db_user               = var.db_user
  tier                  = var.db_tier
  disk_size_gb          = var.db_disk_size_gb
  availability_type     = var.db_availability_type
  deletion_protection   = var.db_deletion_protection
  private_network       = module.networking.network_id
  labels                = local.common_labels

  depends_on = [module.networking]
}

module "memorystore" {
  source         = "./modules/memorystore"
  project_id     = var.project_id
  region         = var.region
  environment    = var.environment
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size_gb
  redis_version  = var.redis_version
  authorized_network = module.networking.network_id
  labels         = local.common_labels

  depends_on = [module.networking]
}

module "frontend_service" {
  source                = "./modules/cloud_run_service"
  project_id            = var.project_id
  region                = var.region
  service_name          = var.frontend_service_name
  image                 = var.frontend_image
  service_account_email = module.service_accounts.frontend_email
  container_port        = var.frontend_port
  cpu                   = var.frontend_cpu
  memory                = var.frontend_memory
  min_instances         = var.frontend_min_instances
  max_instances         = var.frontend_max_instances
  env_vars              = merge({ PORT = tostring(var.frontend_port) }, var.frontend_env_vars)
  secret_env            = var.frontend_secret_env
  ingress               = "INGRESS_TRAFFIC_ALL"
  allow_unauthenticated = var.frontend_public
  labels                = local.common_labels

  depends_on = [module.secret_manager, module.service_accounts]
}

module "backend_service" {
  source                = "./modules/cloud_run_service"
  project_id            = var.project_id
  region                = var.region
  service_name          = var.backend_service_name
  image                 = var.backend_image
  service_account_email = module.service_accounts.backend_email
  container_port        = var.backend_port
  cpu                   = var.backend_cpu
  memory                = var.backend_memory
  min_instances         = var.backend_min_instances
  max_instances         = var.backend_max_instances
  env_vars = merge(
    local.backend_default_env,
    { PORT = tostring(var.backend_port) },
    var.backend_env_vars
  )
  secret_env             = merge({ DATABASE_URL = "database-url", API_ADMIN_TOKEN = "api-admin-token" }, var.backend_secret_env)
  ingress                = var.backend_public ? "INGRESS_TRAFFIC_ALL" : "INGRESS_TRAFFIC_INTERNAL_ONLY"
  allow_unauthenticated  = var.backend_public
  vpc_connector          = module.networking.vpc_connector_id
  vpc_egress             = "ALL_TRAFFIC"
  cloud_sql_instances    = [module.cloud_sql.connection_name]
  labels                 = local.common_labels

  depends_on = [module.cloud_sql, module.memorystore, module.frontend_service]
}

module "worker_job" {
  count = var.worker_enabled ? 1 : 0

  source                = "./modules/cloud_run_job"
  project_id            = var.project_id
  region                = var.region
  job_name              = var.worker_job_name
  image                 = var.worker_image
  service_account_email = module.service_accounts.worker_email
  command               = var.worker_command
  cpu                   = var.worker_cpu
  memory                = var.worker_memory
  task_timeout          = var.worker_task_timeout
  max_retries           = var.worker_max_retries
  parallelism           = var.worker_parallelism
  task_count            = var.worker_task_count
  env_vars = merge(
    local.backend_default_env,
    var.worker_env_vars
  )
  secret_env          = merge({ DATABASE_URL = "database-url" }, var.worker_secret_env)
  vpc_connector       = module.networking.vpc_connector_id
  vpc_egress          = "ALL_TRAFFIC"
  cloud_sql_instances = [module.cloud_sql.connection_name]
  labels              = local.common_labels

  depends_on = [module.cloud_sql, module.memorystore]
}
