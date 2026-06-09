variable "aws_region" {
  default = "eu-central-1"
}

variable "project_name" {
  default = "eventflow"
}

variable "s3_bucket_name" {
  default = "eventflow-banners"
}

variable "ses_sender_email" {
  default = "d.domnich002@gmail.com"
}

variable "environment" {
  default = "dev"
}

variable "db_password" {
  sensitive = true
}
