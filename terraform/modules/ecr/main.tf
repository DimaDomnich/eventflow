resource "aws_ecr_repository" "thumbnail_lambda" {
  name = "eventflow-thumbnail-lambda"

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_repository" "app" {
  name = "${var.project_name}-app"

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
