resource "aws_sesv2_email_identity" "sender" {
  email_identity = var.ses_sender_email

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}
