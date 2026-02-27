variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "db_name" { type = string }
variable "db_user" { type = string }
variable "tier" { type = string }
variable "disk_size_gb" { type = number }
variable "availability_type" { type = string }
variable "deletion_protection" { type = bool }
variable "private_network" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}
