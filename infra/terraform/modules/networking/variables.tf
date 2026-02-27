variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "network_name" { type = string }
variable "subnet_name" { type = string }
variable "subnet_cidr" { type = string }
variable "connector_name" { type = string }
variable "connector_cidr" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}
