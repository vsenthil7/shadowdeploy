# ShadowDeploy harness — generated Terraform
# Well-Architected: Operational Excellence (primary), Reliability, Security.
# Shadow responses are captured for diffing and NEVER served to clients.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = { Project = "ShadowDeploy", Component = "shadow-testing-harness", ManagedBy = "terraform", Environment = "dev" }
  }
}

# --- Capture storage (S3) ---
resource "aws_s3_bucket" "captures" {
  bucket = "shadowdeploy-captures-dev"
}

resource "aws_s3_bucket_lifecycle_configuration" "captures" {
  bucket = aws_s3_bucket.captures.id
  rule {
    id     = "expire-captures"
    status = "Enabled"
    expiration {
      days = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "captures" {
  bucket                  = aws_s3_bucket.captures.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Least-privilege role for the comparison Lambda ---
resource "aws_iam_role" "compare" {
  name = "shadowdeploy-compare-dev"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "compare" {
  name = "shadowdeploy-compare-least-priv"
  role = aws_iam_role.compare.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.captures.arn}/*"
    }]
  })
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
}

# --- Sampling configuration (consumed by the mirror handler) ---
locals {
  sampling_rate  = 0.05
  shadow_enabled = true
  service_type   = "rest_api"
}

