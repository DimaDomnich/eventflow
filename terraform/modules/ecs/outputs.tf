output "ecs_task_execution_role_arn" {
  value = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_security_group_id" {
  value = aws_security_group.ecs_tasks.id
}
