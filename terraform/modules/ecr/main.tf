resource "aws_ecr_repository" "thumbnail_lambda" {
  name = "eventflow-thumbnail-lambda"

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
