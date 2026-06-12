

resource "aws_ecs_task_definition" "web" {
  family                   = "${var.project_name}-${var.environment}-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "web"
      image = "${var.ecr_repository_url}:latest"
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = var.db_url_arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = var.secret_key_arn
        },
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = var.jwt_secret_key_arn
        }
      ]
      environment = [
        { name = "FLASK_ENV", value = var.environment },
        { name = "REDIS_URL", value = "redis://${var.redis_url}:6379/0" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "S3_BUCKET", value = var.s3_bucket },
        { name = "SES_SENDER", value = var.ses_sender },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "web"
        }
      }
    }
  ])

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-${var.environment}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name    = "worker"
      image   = "${var.ecr_repository_url}:latest"
      command = ["celery", "-A", "worker.celery", "worker", "--loglevel=info"]
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = var.db_url_arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = var.secret_key_arn
        },
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = var.jwt_secret_key_arn
        }
      ]
      environment = [
        { name = "FLASK_ENV", value = var.environment },
        { name = "REDIS_URL", value = "redis://${var.redis_url}:6379/0" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "SES_SENDER", value = var.ses_sender },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_task_definition" "beat" {
  family                   = "${var.project_name}-${var.environment}-beat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name    = "beat"
      image   = "${var.ecr_repository_url}:latest"
      command = ["celery", "-A", "worker.celery", "beat", "--loglevel=info"]
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = var.db_url_arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = var.secret_key_arn
        },
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = var.jwt_secret_key_arn
        }
      ]
      environment = [
        { name = "FLASK_ENV", value = var.environment },
        { name = "REDIS_URL", value = "redis://${var.redis_url}:6379/0" },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "beat"
        }
      }
    }
  ])

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
