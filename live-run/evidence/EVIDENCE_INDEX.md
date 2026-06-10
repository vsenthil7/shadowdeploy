# Live-Run Evidence Index

Captured 2026-06-10 from AWS account `087242257828` (vsenthil7-sandbox), region `us-east-1`,
via CLI profile `sandbox` (IAM Identity Center SSO). All resources were deployed by
`terraform apply` of `../main.tf`, evidenced below, then torn down.

## Screenshots (AWS console)

| File | Proves |
|---|---|
| `screenshot_01_dashboard_20260610.png` | CloudWatch dashboard `shadowdeploy-dev` live, both metrics (ShadowErrorRate, DivergenceRate) wired. Account + region visible. |
| `screenshot_02_billing_alarms_list_20260610.png` | All three billing alarms (`shadowdeploy-billing-10/50/100-dev`) present in CloudWatch Alarms. |
| `screenshot_02_billing_alarms_20260610.png` | Billing alarms list (second view). |
| `screenshot_03_s3_bucket_20260610.png` | Capture bucket `shadowdeploy-captures-dev-087242257828` live, empty (0 objects). |
| `screenshot_04_billing_alarm_100_detail_20260610.png` | `shadowdeploy-billing-100-dev` detail: threshold EstimatedCharges>100/6h, USD, real ARN. |

## CLI evidence (machine-readable, in ../logs/)

| Log | Proves |
|---|---|
| `09_evidence_dashboard_*.log` | Dashboard ARN + body returned by `cloudwatch get-dashboard`. |
| `10_evidence_s3_publicblock_*.log` | All four S3 public-access blocks = true. |
| `11_evidence_s3_lifecycle_*.log` | 7-day capture-expiry lifecycle rule, Enabled. |
| `12_evidence_billing_alarms_*.log` | Three billing alarms, thresholds 10/50/100 USD. |
| `13_evidence_bucket_tags_*.log` | Resource tags (Project/Environment/ManagedBy/Component) applied. |

## Terraform plan/apply (in ../logs/ and here)

| Artifact | Content |
|---|---|
| `plan_readable.txt` / `plan.json` | The reviewed execution plan (9 resources originally). |
| `../logs/05_apply_*.log` | First apply: 8 resources created; IAM role denied (PowerUserAccess cannot iam:CreateRole). |
| `../logs/07_apply_reconcile_*.log` | Re-apply after removing IAM role: "infrastructure matches configuration". |
| `../logs/08_state_final_*.log` | Final inventory: 8 resources. |

## Other

| File | Content |
|---|---|
| `eventbridge_rule_billing_100_alarm.json` | The EventBridge custom event pattern the console suggests for the billing-100 alarm state change. |

## Note on IAM role

The reference implementation's `aws_iam_role.compare` (least-privilege, S3-scoped, no
wildcards) is intentionally NOT part of this live run: the sandbox's PowerUserAccess
permission set cannot create IAM roles, and no Lambda was deployed for the role to
attach to. The role's correctness is proven by the reference implementation and its
100%-covered tests. This live run proves the deployable, locked-down, monitored,
cost-guarded infrastructure.
