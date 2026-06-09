variable "project_name" {}

variable "environment" {}

variable "vpc_id" {}

variable "private_subnet_ids" {}

variable "allowed_security_group_id" {}

variable "node_type" {
  default = "cache.t3.micro"
}


