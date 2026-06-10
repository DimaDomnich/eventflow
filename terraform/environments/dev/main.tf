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
  allowed_security_group_id = module.ecs.ecs_security_group_id
  bastion_security_group_id = module.bastion.bastion_security_group_id
}

module "elasti_cache" {
  source                    = "../../modules/elasticache"
  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_subnet_ids        = module.vpc.private_subnet_ids
  allowed_security_group_id = module.ecs.ecs_security_group_id
}


module "alb" {
  source            = "../../modules/alb"
  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}

module "ecs" {
  source                = "../../modules/ecs"
  project_name          = var.project_name
  environment           = var.environment
  ses_sender            = var.ses_sender_email
  aws_region            = var.aws_region
  s3_bucket             = var.s3_bucket_name
  secret_key            = var.secret_key
  jwt_secret_key        = var.jwt_secret_key
  db_url                = module.rds.db_endpoint
  redis_url             = module.elasti_cache.redis_endpoint
  ecr_repository_url    = module.ecr.app_repository_url
  private_subnet_ids    = module.vpc.private_subnet_ids
  public_subnet_ids     = module.vpc.public_subnet_ids
  vpc_id                = module.vpc.vpc_id
  target_group_arn      = module.alb.target_group_arn
  alb_security_group_id = module.alb.alb_security_group_id
  db_password           = var.db_password
}

module "bastion" {
  source           = "../../modules/bastion"
  project_name     = var.project_name
  environment      = var.environment
  allowed_ip       = var.allowed_ip
  public_subnet_id = module.vpc.public_subnet_ids[0]
  vpc_id           = module.vpc.vpc_id
}
