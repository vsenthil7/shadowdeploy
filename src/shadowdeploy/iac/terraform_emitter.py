"""Terraform emitter for the ShadowDeploy harness.

Generates a Terraform configuration string for the mirroring + capture + diff
storage + dashboard resources. Every resource is tagged; IAM is least-privilege
scoped to the named buckets/functions; billing alerts are included.

This is deterministic string generation (no cloud calls) so it is fully
testable and never touches AWS.
"""
from __future__ import annotations

import json

from ..core.models import MirrorConfig

REQUIRED_TAGS = ("Project", "Component", "ManagedBy", "Environment")


def emit_terraform(config: MirrorConfig, *, environment: str = "dev") -> str:
    """Return a Terraform HCL string for the harness."""
    if not environment.strip():
        raise ValueError("environment must be non-empty")

    tags = {
        "Project": "ShadowDeploy",
        "Component": "shadow-testing-harness",
        "ManagedBy": "terraform",
        "Environment": environment,
    }
    tags_hcl = _hcl_map(tags)
    bucket = f"shadowdeploy-captures-{environment}"

    return f"""# ShadowDeploy harness — generated Terraform
# Well-Architected: Operational Excellence (primary), Reliability, Security.
# Shadow responses are captured for diffing and NEVER served to clients.

terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{config.region}"
  default_tags {{
    tags = {tags_hcl}
  }}
}}

# --- Capture storage (S3) ---
resource "aws_s3_bucket" "captures" {{
  bucket = "{bucket}"
}}

resource "aws_s3_bucket_lifecycle_configuration" "captures" {{
  bucket = aws_s3_bucket.captures.id
  rule {{
    id     = "expire-captures"
    status = "Enabled"
    expiration {{
      days = {config.log_retention_days}
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "captures" {{
  bucket                  = aws_s3_bucket.captures.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

# --- Least-privilege role for the comparison Lambda ---
resource "aws_iam_role" "compare" {{
  name = "shadowdeploy-compare-{environment}"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {{ Service = "lambda.amazonaws.com" }}
    }}]
  }})
}}

resource "aws_iam_role_policy" "compare" {{
  name = "shadowdeploy-compare-least-priv"
  role = aws_iam_role.compare.id
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${{aws_s3_bucket.captures.arn}}/*"
    }}]
  }})
}}

# --- CloudWatch dashboard: shadow error rate + divergence ---
resource "aws_cloudwatch_dashboard" "shadow" {{
  dashboard_name = "shadowdeploy-{environment}"
  dashboard_body = jsonencode({{
    widgets = [{{
      type = "metric"
      properties = {{
        title   = "Shadow error rate & divergence"
        metrics = [["ShadowDeploy", "ShadowErrorRate"], ["ShadowDeploy", "DivergenceRate"]]
        region  = "{config.region}"
      }}
    }}]
  }})
}}

# --- Cost governance: billing alerts at $10/$50/$100 ---
{_billing_alarms(environment)}

# --- Sampling configuration (consumed by the mirror handler) ---
locals {{
  sampling_rate  = {config.sampling_rate}
  shadow_enabled = {str(config.shadow_enabled).lower()}
  service_type   = "{config.service_type.value}"
}}
"""


def _billing_alarms(environment: str) -> str:
    blocks = []
    for threshold in (10, 50, 100):
        blocks.append(
            f"""resource "aws_cloudwatch_metric_alarm" "billing_{threshold}" {{
  alarm_name          = "shadowdeploy-billing-{threshold}-{environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600
  statistic           = "Maximum"
  threshold           = {threshold}
}}"""
        )
    return "\n\n".join(blocks)


def _hcl_map(d: dict) -> str:
    # Render a flat string map as HCL.
    inner = ", ".join(f'{k} = {json.dumps(v)}' for k, v in d.items())
    return "{ " + inner + " }"
