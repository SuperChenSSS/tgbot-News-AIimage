data "hcp_vault_secrets_app" "web_application" {
  app_name = "chatbot-kv"
}

locals {
  secrets_map = data.hcp_vault_secrets_app.web_application.secrets
}