resource "google_redis_instance" "main" {
  project            = var.project_id
  region             = var.region
  name               = "pulsewire-${var.environment}-redis"
  tier               = var.tier
  memory_size_gb     = var.memory_size_gb
  redis_version      = var.redis_version
  authorized_network = var.authorized_network
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  labels = var.labels
}
