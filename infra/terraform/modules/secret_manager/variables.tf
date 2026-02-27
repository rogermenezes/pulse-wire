variable "project_id" { type = string }
variable "environment" { type = string }
variable "secrets" { type = list(string) }
variable "labels" {
  type    = map(string)
  default = {}
}
