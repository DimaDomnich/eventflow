resource "aws_lambda_function" "thumbnail" {
  function_name = "eventflow-thumbnail"
  role          = var.lambda_role_arn
  package_type  = "Image"
  image_uri     = "${var.ecr_repository_url}:latest"
  timeout       = 30

  environment {
    variables = {
      S3_BUCKET = var.s3_bucket_name
    }
  }

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
