# The Telegram bot token, created by hand in Secrets Manager (never destroyed).
# Terraform only looks it up, so the token itself never enters the Terraform state.
data "aws_secretsmanager_secret" "telegram" {
  name = "news-bot/telegram"
}