output "frontend_email" {
  value = google_service_account.accounts["frontend"].email
}

output "backend_email" {
  value = google_service_account.accounts["backend"].email
}

output "worker_email" {
  value = google_service_account.accounts["worker"].email
}
