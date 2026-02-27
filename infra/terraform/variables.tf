variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "prod"
}

variable "labels" {
  description = "Common labels applied to resources"
  type        = map(string)
  default     = {}
}

variable "frontend_image" {
  description = "Artifact Registry image URL for frontend"
  type        = string
}

variable "backend_image" {
  description = "Artifact Registry image URL for backend"
  type        = string
}

variable "worker_image" {
  description = "Artifact Registry image URL for worker job"
  type        = string
}

variable "frontend_service_name" {
  type    = string
  default = "pulsewire-web"
}

variable "backend_service_name" {
  type    = string
  default = "pulsewire-api"
}

variable "worker_job_name" {
  type    = string
  default = "pulsewire-worker"
}

variable "frontend_cpu" {
  type    = string
  default = "1"
}

variable "frontend_memory" {
  type    = string
  default = "512Mi"
}

variable "backend_cpu" {
  type    = string
  default = "1"
}

variable "backend_memory" {
  type    = string
  default = "1024Mi"
}

variable "worker_cpu" {
  type    = string
  default = "1"
}

variable "worker_memory" {
  type    = string
  default = "1024Mi"
}

variable "frontend_min_instances" {
  type    = number
  default = 0
}

variable "frontend_max_instances" {
  type    = number
  default = 3
}

variable "backend_min_instances" {
  type    = number
  default = 0
}

variable "backend_max_instances" {
  type    = number
  default = 5
}

variable "frontend_port" {
  type    = number
  default = 3000
}

variable "backend_port" {
  type    = number
  default = 8000
}

variable "frontend_public" {
  type    = bool
  default = true
}

variable "backend_public" {
  type    = bool
  default = true
}

variable "db_name" {
  type    = string
  default = "pulsewire"
}

variable "db_user" {
  type    = string
  default = "pulsewire"
}

variable "db_tier" {
  type    = string
  default = "db-custom-1-3840"
}

variable "db_disk_size_gb" {
  type    = number
  default = 20
}

variable "db_availability_type" {
  type    = string
  default = "ZONAL"
}

variable "db_deletion_protection" {
  type    = bool
  default = true
}

variable "redis_tier" {
  type    = string
  default = "STANDARD_HA"
}

variable "redis_memory_size_gb" {
  type    = number
  default = 1
}

variable "redis_version" {
  type    = string
  default = "REDIS_7_2"
}

variable "vpc_name" {
  type    = string
  default = "pulsewire-vpc"
}

variable "subnet_name" {
  type    = string
  default = "pulsewire-subnet"
}

variable "subnet_cidr" {
  type    = string
  default = "10.20.0.0/24"
}

variable "vpc_connector_name" {
  type    = string
  default = "pulsewire-serverless-connector"
}

variable "vpc_connector_cidr" {
  type    = string
  default = "10.8.0.0/28"
}

variable "worker_enabled" {
  type    = bool
  default = true
}

variable "worker_command" {
  description = "Command for Cloud Run Job"
  type        = list(string)
  default     = ["python", "job_runner.py"]
}

variable "worker_task_timeout" {
  type    = string
  default = "1800s"
}

variable "worker_max_retries" {
  type    = number
  default = 1
}

variable "worker_parallelism" {
  type    = number
  default = 1
}

variable "worker_task_count" {
  type    = number
  default = 1
}

variable "frontend_env_vars" {
  type    = map(string)
  default = {}
}

variable "backend_env_vars" {
  type    = map(string)
  default = {}
}

variable "worker_env_vars" {
  type    = map(string)
  default = {}
}

variable "frontend_secret_env" {
  description = "Map env var name => Secret Manager secret id"
  type        = map(string)
  default     = {}
}

variable "backend_secret_env" {
  description = "Map env var name => Secret Manager secret id"
  type        = map(string)
  default     = {}
}

variable "worker_secret_env" {
  description = "Map env var name => Secret Manager secret id"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secret Manager secret ids to provision"
  type        = list(string)
  default = [
    "database-url",
    "openai-api-key",
    "anthropic-api-key",
    "reddit-client-id",
    "reddit-client-secret",
    "discord-bot-token",
    "api-admin-token"
  ]
}
