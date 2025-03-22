terraform {
  cloud {
    organization = "my_chen"
    workspaces {
      name = "chatbot"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    hcp = {
      source  = "hashicorp/hcp"
      version = "~>0.104.0"
    }
  }
  required_version = ">= 0.14.9"
}

provider "aws" {
  region     = var.aws_region
  access_key = var.key_id
  secret_key = var.key_secret
}

module "my_hcp" {
  source = "./modules/hcp"
}

resource "aws_ecr_repository" "chatbot_ecr" {
  name = var.ecr_repo_name
}

data "aws_caller_identity" "current" {}

# IAM Role
resource "aws_iam_role" "apprunner_role" {
  name = "apprunner-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = [
            "build.apprunner.amazonaws.com",
            "tasks.apprunner.amazonaws.com"
          ]
        },
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner_attach" {
  role       = aws_iam_role.apprunner_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

data "aws_secretsmanager_secret" "existing_secret" {
  name  = var.secrets
  count = 1
}

resource "aws_secretsmanager_secret_version" "chatbot_secrets_version" {
  secret_id     = data.aws_secretsmanager_secret.existing_secret[0].id
  secret_string = jsonencode(module.my_hcp.secrets_map)
}

resource "aws_iam_policy" "secrets_access" {
  name        = "app-runner-secrets-access"
  description = "Allow App Runner to access secrets"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
        ],
        Effect   = "Allow",
        Resource = data.aws_secretsmanager_secret.existing_secret[0].arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_attach" {
  role       = aws_iam_role.apprunner_role.id
  policy_arn = aws_iam_policy.secrets_access.arn
}

resource "time_sleep" "waitrolecreate" {
  depends_on      = [aws_iam_role.apprunner_role]
  create_duration = "60s"
}

resource "aws_apprunner_auto_scaling_configuration_version" "chatbot" {
  auto_scaling_configuration_name = "chatbot-apprunner-autoscaling"

  max_concurrency = 100
  max_size        = 1
  min_size        = 1

  tags = {
    Name = "chatbot-apprunner-autoscaling"
  }
}

# Create App Runner Service
resource "aws_apprunner_service" "chatbot_apprunner" {
  depends_on   = [time_sleep.waitrolecreate]
  service_name = var.chatbot-runner
  source_configuration {
    image_repository {
      image_repository_type = "ECR"
      image_identifier      = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repo_name}:latest"
      image_configuration {
        port = "80"
        runtime_environment_secrets = {
          for key in keys(module.my_hcp.secrets_map) :
          key => "${data.aws_secretsmanager_secret.existing_secret[0].arn}:${key}::"
        }
      }
    }
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_role.arn
    }
  }
  health_check_configuration {
    protocol = "HTTP"
    path     = "/health_cmy"
    interval = 20
  }
  instance_configuration {
    cpu               = "0.25 vCPU"
    memory            = "0.5 GB"
    instance_role_arn = aws_iam_role.apprunner_role.arn
  }
  network_configuration {
    egress_configuration {
      egress_type = "DEFAULT"
    }
  }
  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.chatbot.arn
}