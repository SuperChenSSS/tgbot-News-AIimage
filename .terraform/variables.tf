variable "aws_region" {
  type    = string
  default = "ap-southeast-1" #Singapore
}

variable "ecr_repo_name" {
  type    = string
  default = "chatbot"
}

variable "image_name" {
  type    = string
  default = "chatbot"
}

variable "key_id" {
  type    = string
  default = ""
}

variable "key_secret" {
  type    = string
  default = ""
}

variable "secrets" {
  type    = string
  default = "chatbot-secrets"
  
}

variable "chatbot-runner" {
  type    = string
  default = "chatbot-apprunner"
}