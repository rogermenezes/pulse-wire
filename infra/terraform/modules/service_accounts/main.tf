locals {
  accounts = {
    frontend = "pulsewire-${var.environment}-frontend-sa"
    backend  = "pulsewire-${var.environment}-backend-sa"
    worker   = "pulsewire-${var.environment}-worker-sa"
  }
}

resource "google_service_account" "accounts" {
  for_each     = local.accounts
  project      = var.project_id
  account_id   = each.value
  display_name = "PulseWire ${each.key} (${var.environment})"
}

resource "google_project_iam_member" "frontend_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.accounts["frontend"].email}"
}

resource "google_project_iam_member" "backend_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.accounts["backend"].email}"
}

resource "google_project_iam_member" "worker_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.accounts["worker"].email}"
}

resource "google_project_iam_member" "backend_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.accounts["backend"].email}"
}

resource "google_project_iam_member" "worker_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.accounts["worker"].email}"
}

resource "google_project_iam_member" "backend_vpc_user" {
  project = var.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:${google_service_account.accounts["backend"].email}"
}

resource "google_project_iam_member" "worker_vpc_user" {
  project = var.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:${google_service_account.accounts["worker"].email}"
}

resource "google_project_iam_member" "backend_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.accounts["backend"].email}"
}

resource "google_project_iam_member" "worker_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.accounts["worker"].email}"
}

resource "google_project_iam_member" "frontend_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.accounts["frontend"].email}"
}

resource "google_project_iam_member" "backend_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.accounts["backend"].email}"
}

resource "google_project_iam_member" "worker_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.accounts["worker"].email}"
}
