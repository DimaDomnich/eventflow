terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket       = "eventflow-terraform-state-270278217201"
    key          = "eventflow/terraform.tfstate"
    region       = "eu-central-1"
    use_lockfile = true
    encrypt      = true
  }
}

provider "aws" {
  region = var.aws_region
}

module "s3" {
  source         = "../../modules/s3"
  project_name   = var.project_name
  s3_bucket_name = var.s3_bucket_name
}

module "iam" {
  source         = "../../modules/iam"
  project_name   = var.project_name
  s3_bucket_name = var.s3_bucket_name
}

module "lambda" {
  source             = "../../modules/lambda"
  project_name       = var.project_name
  s3_bucket_name     = var.s3_bucket_name
  lambda_role_arn    = module.iam.lambda_role_arn
  ecr_repository_url = module.ecr.repository_url
}

module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
}

module "ses" {
  source           = "../../modules/ses"
  project_name     = var.project_name
  ses_sender_email = var.ses_sender_email
}

module "vpc" {
  source       = "../../modules/vpc"
  project_name = var.project_name
  environment  = var.environment
}

module "rds" {
  source                    = "../../modules/rds"
  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_subnet_ids        = module.vpc.private_subnet_ids
  db_password               = var.db_password
  allowed_security_group_id = "" # todo
}
