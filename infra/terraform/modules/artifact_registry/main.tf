locals {
  repos = {
    frontend = "pulsewire-${var.environment}-frontend"
    backend  = "pulsewire-${var.environment}-backend"
    worker   = "pulsewire-${var.environment}-worker"
  }
}

resource "google_artifact_registry_repository" "repos" {
  for_each      = local.repos
  project       = var.project_id
  location      = var.region
  repository_id = each.value
  description   = "${each.key} images for pulsewire ${var.environment}"
  format        = "DOCKER"
  labels        = var.labels
}
