output "frontend_service_url" {
  value       = module.frontend_service.url
  description = "Public URL of frontend Cloud Run service"
}

output "backend_service_url" {
  value       = module.backend_service.url
  description = "Public URL of backend Cloud Run service"
}

output "cloud_sql_instance_name" {
  value       = module.cloud_sql.instance_name
  description = "Cloud SQL instance name"
}

output "cloud_sql_connection_name" {
  value       = module.cloud_sql.connection_name
  description = "Cloud SQL connection name (for Cloud Run socket connector)"
}

output "cloud_sql_private_ip" {
  value       = module.cloud_sql.private_ip
  description = "Cloud SQL private IP"
}

output "database_name" {
  value       = module.cloud_sql.database_name
  description = "App database name"
}

output "redis_host" {
  value       = module.memorystore.host
  description = "Memorystore Redis host"
}

output "redis_port" {
  value       = module.memorystore.port
  description = "Memorystore Redis port"
}

output "artifact_registry_repositories" {
  value = {
    frontend = module.artifact_registry.frontend_repository
    backend  = module.artifact_registry.backend_repository
    worker   = module.artifact_registry.worker_repository
  }
  description = "Artifact Registry repository ids"
}

output "service_accounts" {
  value = {
    frontend = module.service_accounts.frontend_email
    backend  = module.service_accounts.backend_email
    worker   = module.service_accounts.worker_email
  }
  description = "Runtime service account emails"
}

output "worker_job_name" {
  value       = var.worker_enabled ? module.worker_job[0].name : null
  description = "Cloud Run Job name for worker tasks"
}

output "secret_ids" {
  value       = module.secret_manager.secret_ids
  description = "Secret Manager secret IDs provisioned"
}
