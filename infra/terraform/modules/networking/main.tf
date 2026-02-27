resource "google_compute_network" "main" {
  project                 = var.project_id
  name                    = "${var.network_name}-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  project       = var.project_id
  name          = "${var.subnet_name}-${var.environment}"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id
}

# Private Service Access block for Cloud SQL private IP.
resource "google_compute_global_address" "private_service_access" {
  project       = var.project_id
  name          = "pulsewire-${var.environment}-private-service-access"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_service_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_access.name]
}

resource "google_vpc_access_connector" "serverless" {
  project       = var.project_id
  name          = "${var.connector_name}-${var.environment}"
  region        = var.region
  network       = google_compute_network.main.name
  ip_cidr_range = var.connector_cidr
  min_instances = 2
  max_instances = 3
}
