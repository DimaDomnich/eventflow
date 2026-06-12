output "db_password_arn" {
  value = aws_secretsmanager_secret.db_password.arn
}

output "secret_key_arn" {
  value = aws_secretsmanager_secret.secret_key.arn
}

output "jwt_secret_key_arn" {
  value = aws_secretsmanager_secret.jwt_secret_key.arn
}

output "db_url_arn" {
  value = aws_secretsmanager_secret.db_url.arn
}
