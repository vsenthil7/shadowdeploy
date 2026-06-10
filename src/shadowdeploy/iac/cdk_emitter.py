"""AWS CDK (TypeScript) emitter for the ShadowDeploy harness.

Generates a CDK stack string. Like the Terraform emitter, this is deterministic
string generation — no cloud calls, fully testable.
"""
from __future__ import annotations

from ..core.models import MirrorConfig


def emit_cdk(config: MirrorConfig, *, environment: str = "dev") -> str:
    """Return a CDK TypeScript stack string for the harness."""
    if not environment.strip():
        raise ValueError("environment must be non-empty")

    bucket = f"shadowdeploy-captures-{environment}"
    return f"""// ShadowDeploy harness — generated AWS CDK (TypeScript)
// Well-Architected: Operational Excellence (primary), Reliability, Security.
// Shadow responses are captured for diffing and NEVER served to clients.
import * as cdk from 'aws-cdk-lib';
import {{ Construct }} from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cw from 'aws-cdk-lib/aws-cloudwatch';

export class ShadowDeployStack extends cdk.Stack {{
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {{
    super(scope, id, props);

    cdk.Tags.of(this).add('Project', 'ShadowDeploy');
    cdk.Tags.of(this).add('Component', 'shadow-testing-harness');
    cdk.Tags.of(this).add('ManagedBy', 'cdk');
    cdk.Tags.of(this).add('Environment', '{environment}');

    const captures = new s3.Bucket(this, 'Captures', {{
      bucketName: '{bucket}',
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      lifecycleRules: [{{ expiration: cdk.Duration.days({config.log_retention_days}) }}],
    }});

    const compareRole = new iam.Role(this, 'CompareRole', {{
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    }});
    // Least-privilege: only read/write the capture bucket objects.
    captures.grantReadWrite(compareRole);

    new cw.Dashboard(this, 'ShadowDashboard', {{
      dashboardName: 'shadowdeploy-{environment}',
    }}).addWidgets(
      new cw.GraphWidget({{
        title: 'Shadow error rate & divergence',
        left: [
          new cw.Metric({{ namespace: 'ShadowDeploy', metricName: 'ShadowErrorRate' }}),
          new cw.Metric({{ namespace: 'ShadowDeploy', metricName: 'DivergenceRate' }}),
        ],
      }}),
    );

    // Cost governance: billing alarms at $10 / $50 / $100.
    for (const threshold of [10, 50, 100]) {{
      new cw.Alarm(this, `Billing${{threshold}}`, {{
        metric: new cw.Metric({{
          namespace: 'AWS/Billing',
          metricName: 'EstimatedCharges',
          statistic: 'Maximum',
          period: cdk.Duration.hours(6),
        }}),
        threshold,
        evaluationPeriods: 1,
        comparisonOperator: cw.ComparisonOperator.GREATER_THAN_THRESHOLD,
      }});
    }}

    // Sampling configuration consumed by the mirror handler.
    new cdk.CfnOutput(this, 'SamplingRate', {{ value: '{config.sampling_rate}' }});
    new cdk.CfnOutput(this, 'ShadowEnabled', {{ value: '{str(config.shadow_enabled).lower()}' }});
  }}
}}
"""
