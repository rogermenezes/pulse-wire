variable "project_id" { type = string }
variable "region" { type = string }
variable "job_name" { type = string }
variable "image" { type = string }
variable "service_account_email" { type = string }
variable "command" {
  type    = list(string)
  default = []
}
variable "cpu" { type = string }
variable "memory" { type = string }
variable "task_timeout" { type = string }
variable "max_retries" { type = number }
variable "parallelism" { type = number }
variable "task_count" { type = number }
variable "env_vars" {
  type    = map(string)
  default = {}
}
variable "secret_env" {
  type    = map(string)
  default = {}
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
