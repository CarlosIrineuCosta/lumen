variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
  default     = "lumen-photography-platform"
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "billing_account" {
  description = "Google Cloud Billing Account ID"
  type        = string
}

variable "notification_email" {
  description = "Email for budget alerts"
  type        = string
}
