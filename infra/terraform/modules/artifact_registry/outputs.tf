output "frontend_repository" {
  value = google_artifact_registry_repository.repos["frontend"].repository_id
}

output "backend_repository" {
  value = google_artifact_registry_repository.repos["backend"].repository_id
}

output "worker_repository" {
  value = google_artifact_registry_repository.repos["worker"].repository_id
}
