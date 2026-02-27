variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "tier" { type = string }
variable "memory_size_gb" { type = number }
variable "redis_version" { type = string }
variable "authorized_network" { type = string }
variable "labels" {
  type    = map(string)
  default = {}
}
