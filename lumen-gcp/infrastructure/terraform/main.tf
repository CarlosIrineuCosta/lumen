terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  service = each.value
  project = var.project_id
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "lumen_db" {
  name             = "lumen-db"
  database_version = "POSTGRES_15"
  region          = var.region

  settings {
    tier = "db-f1-micro"  # Free tier eligible
    
    backup_configuration {
      enabled = true
    }
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        value = "0.0.0.0/0"  # Restrict this in production
      }
    }
  }

  deletion_protection = false
}

# Cloud Storage buckets
resource "google_storage_bucket" "user_uploads" {
  name     = "${var.project_id}-user-uploads"
  location = "US"
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "static_assets" {
  name     = "${var.project_id}-static-assets"
  location = "US"
  
  website {
    main_page_suffix = "index.html"
  }
}

# Cloud Monitoring budget alert
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"
  
  labels = {
    email_address = var.notification_email
  }
}

resource "google_billing_budget" "lumen_budget" {
  billing_account = var.billing_account
  display_name    = "Lumen Project Budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "100"  # $100 budget
    }
  }

  threshold_rules {
    threshold_percent = 0.5  # 50% threshold
  }
  
  threshold_rules {
    threshold_percent = 0.9  # 90% threshold
  }

  all_updates_rule {
    notification_channels = [google_monitoring_notification_channel.email.id]
    disable_default_iam_recipients = false
  }
}
