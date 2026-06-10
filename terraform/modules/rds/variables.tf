variable "project_name" {}
variable "environment" {}
variable "vpc_id" {}
variable "private_subnet_ids" {}
variable "bastion_security_group_id" {}

variable "db_name" {
  default = "eventflow"
}

variable "db_username" {
  default = "eventflow"
}

variable "db_password" {
  sensitive = true
}

variable "db_instance_class" {
  default = "db.t3.micro"
}

variable "allowed_security_group_id" {}
