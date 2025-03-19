output "ecr_repository_url" {
  value       = aws_ecr_repository.chatbot_ecr.repository_url
  description = "The URL of the ECR repository."
}

output "apprunner_service_url" {
  value       = aws_apprunner_service.chatbot_apprunner.service_url
  description = "The URL of the App Runner service."
}

output "apprunner_service_arn" {
  value       = aws_apprunner_service.chatbot_apprunner.arn
  description = "The ARN of the App Runner service."
}