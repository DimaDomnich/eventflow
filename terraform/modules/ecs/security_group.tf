
resource "aws_security_group" "ecs_tasks" {
  name   = "${var.project_name}-${var.environment}-ecs_tasks-sg"
  vpc_id = var.vpc_id


  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }



  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-tasks-sg"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
