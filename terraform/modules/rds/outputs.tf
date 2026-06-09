output "db_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "rds_security_group_id" {
  value = aws_security_group.rds.id
}
