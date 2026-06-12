variable "project_name" {}
variable "environment" {}
variable "db_password" {
  sensitive = true
}
variable "secret_key" {
  sensitive = true
}
variable "jwt_secret_key" {
  sensitive = true
}
variable "db_url" {
  sensitive = true
}
