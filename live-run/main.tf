# ShadowDeploy harness — LIVE RUN copy (derived from infra/terraform/main.tf)
# Deployed to us-east-1 because AWS/Billing EstimatedCharges metrics only exist there.
# Bucket name suffixed with account id for global uniqueness.
# Shadow responses are captured for diffing and NEVER served to clients.
#
# NOTE (live-run scope): the aws_iam_role.compare + its policy from the reference
# impl are intentionally OMITTED here. PowerUserAccess (this sandbox's permission
# set) cannot create IAM roles, and there is no Lambda deployed in this demo for
# the role to attach to. The role's least-privilege definition is proven in the
# reference implementation and its tests (../infra/terraform/main.tf, 100% covered).
# This live run proves the deployable, locked-down, monitored, cost-guarded infra.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "sandbox"
  default_tags {
    tags = { Project = "ShadowDeploy", Component = "shadow-testing-harness", ManagedBy = "terraform", Environment = "dev" }
  }
}

data "aws_caller_identity" "current" {}

# --- Capture storage (S3) ---
resource "aws_s3_bucket" "captures" {
  bucket = "shadowdeploy-captures-dev-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_lifecycle_configuration" "captures" {
  bucket = aws_s3_bucket.captures.id
  rule {
    id     = "expire-captures"
    status = "Enabled"
    expiration {
      days = 7
    }
    filter {}
  }
}

resource "aws_s3_bucket_public_access_block" "captures" {
  bucket                  = aws_s3_bucket.captures.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- CloudWatch dashboard: shadow error rate + divergence ---
resource "aws_cloudwatch_dashboard" "shadow" {
  dashboard_name = "shadowdeploy-dev"
  dashboard_body = jsonencode({
    widgets = [{
      type = "metric"
      properties = {
        title   = "Shadow error rate & divergence"
        metrics = [["ShadowDeploy", "ShadowErrorRate"], ["ShadowDeploy", "DivergenceRate"]]
        region  = "us-east-1"
      }
    }]
  })
}

# --- Cost governance: billing alerts at $10/$50/$100 ---
resource "aws_cloudwatch_metric_alarm" "billing_10" {
  alarm_name          = "shadowdeploy-billing-10-dev"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = 10
  dimensions          = { Currency = "USD" }
}

resource "aws_cloudwatch_metric_alarm" "billing_50" {
  alarm_name          = "shadowdeploy-billing-50-dev"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = 50
  dimensions          = { Currency = "USD" }
}

resource "aws_cloudwatch_metric_alarm" "billing_100" {
  alarm_name          = "shadowdeploy-billing-100-dev"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = 100
  dimensions          = { Currency = "USD" }
}

# --- Sampling configuration (consumed by the mirror handler) ---
locals {
  sampling_rate  = 0.05
  shadow_enabled = true
  service_type   = "rest_api"
}

output "captures_bucket" {
  value = aws_s3_bucket.captures.id
}

output "dashboard_name" {
  value = aws_cloudwatch_dashboard.shadow.dashboard_name
}
