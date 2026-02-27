resource "google_cloud_run_v2_job" "main" {
  project  = var.project_id
  name     = var.job_name
  location = var.region
  labels   = var.labels

  template {
    template {
      service_account = var.service_account_email
      timeout         = var.task_timeout
      max_retries     = var.max_retries

      dynamic "vpc_access" {
        for_each = var.vpc_connector == null ? [] : [var.vpc_connector]
        content {
          connector = vpc_access.value
          egress    = var.vpc_egress
        }
      }

      dynamic "volumes" {
        for_each = length(var.cloud_sql_instances) == 0 ? [] : [1]
        content {
          name = "cloudsql"
          cloud_sql_instance {
            instances = var.cloud_sql_instances
          }
        }
      }

      containers {
        image   = var.image
        command = var.command

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }

        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.key
            value = env.value
          }
        }

        dynamic "env" {
          for_each = var.secret_env
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }

        dynamic "volume_mounts" {
          for_each = length(var.cloud_sql_instances) == 0 ? [] : [1]
          content {
            name       = "cloudsql"
            mount_path = "/cloudsql"
          }
        }
      }
    }

    parallelism = var.parallelism
    task_count  = var.task_count
  }
}
