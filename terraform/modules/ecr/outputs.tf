output "repository_url" {
  value = aws_ecr_repository.thumbnail_lambda.repository_url
}

output "app_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
