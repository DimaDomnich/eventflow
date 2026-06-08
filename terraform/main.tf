terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

}

provider "aws" {
  region = var.aws_region
}

module "s3" {
  source         = "./modules/s3"
  project_name   = var.project_name
  s3_bucket_name = var.s3_bucket_name
}

module "iam" {
  source         = "./modules/iam"
  project_name   = var.project_name
  s3_bucket_name = var.s3_bucket_name
}

module "lambda" {
  source             = "./modules/lambda"
  project_name       = var.project_name
  s3_bucket_name     = var.s3_bucket_name
  lambda_role_arn    = module.iam.lambda_role_arn
  ecr_repository_url = module.ecr.repository_url
}

module "ecr" {
  source       = "./modules/ecr"
  project_name = var.project_name
}

module "ses" {
  source           = "./modules/ses"
  project_name     = var.project_name
  ses_sender_email = var.ses_sender_email
}
