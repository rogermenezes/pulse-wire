variable "project_id" { type = string }
variable "region" { type = string }
variable "service_name" { type = string }
variable "image" { type = string }
variable "service_account_email" { type = string }
variable "container_port" { type = number }
variable "cpu" { type = string }
variable "memory" { type = string }
variable "min_instances" { type = number }
variable "max_instances" { type = number }
variable "env_vars" {
  type    = map(string)
  default = {}
}
variable "secret_env" {
  description = "Map env var => Secret Manager secret id"
  type        = map(string)
  default     = {}
}
variable "ingress" {
  type    = string
  default = "INGRESS_TRAFFIC_ALL"
}
variable "allow_unauthenticated" {
  type    = bool
  default = true
}
variable "vpc_connector" {
  type    = string
  default = null
}
variable "vpc_egress" {
  type    = string
  default = null
}
variable "cloud_sql_instances" {
  type    = list(string)
  default = []
}
variable "labels" {
  type    = map(string)
  default = {}
}
