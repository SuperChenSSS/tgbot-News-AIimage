terraform {
#   cloud {
#     organization = "my_chen"
#     workspaces {
#       name = "chatbot"
#     }
#   }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 0.14.9"
}

provider "aws" {
  region     = var.aws_region
#   access_key = var.key_id
#   secret_key = var.key_secret
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
          Service = "build.apprunner.amazonaws.com"
        },
        Effect = "Allow"
      }
    ]
  })
}

# Assign IAM policy to the role
resource "aws_iam_policy" "apprunner_policy" {
  name        = "apprunner-policy"
  description = "IAM policy for App Runner access"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage"
        ],
        Effect = "Allow",
        Resource = [
          aws_ecr_repository.chatbot_ecr.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner_attach" {
  role       = aws_iam_role.apprunner_role.name
  policy_arn = aws_iam_policy.apprunner_policy.arn
}

locals {
  secrets = file("secrets.txt")
  secrets_map = { for pair in regexall("([A-Za-z0-9_]+)=([A-Za-z0-9_\\-\\.:/]+)", local.secrets) : pair[0] => pair[1] }
}

# Create App Runner Service
resource "aws_apprunner_service" "chatbot_apprunner" {
  service_name = "chatbot-apprunner"
  source_configuration {
    image_repository {
      image_repository_type = "ECR"
      image_identifier = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_repo_name}:latest"
      image_configuration {
        port = "80" # port: 80
        runtime_environment_variables = local.secrets_map
      }
    }
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_role.arn
    }
  }
  network_configuration {
    egress_configuration {
      egress_type = "DEFAULT"
    }
  }
}