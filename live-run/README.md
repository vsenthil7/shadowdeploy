# ShadowDeploy — Live AWS Run (Evidence)

This folder contains the **live AWS validation** of the ShadowDeploy reference
implementation: the actual Terraform deployed to a real AWS sandbox account, with
every command and its full output captured for audit.

It exists to close the one gap the offline test suite cannot: proving the
infrastructure the prompt describes **actually deploys and behaves as claimed**
in a real account — not just that the Python passes tests.

## Account / region

- AWS account: `087242257828` (vsenthil7-sandbox, dedicated sandbox)
- Region: `us-east-1` (required: AWS/Billing `EstimatedCharges` metrics only exist there)
- Auth: IAM Identity Center SSO, CLI profile `sandbox` (no long-lived secret on disk)

## What's here

- `main.tf` — the live-run Terraform. Derived from `../infra/terraform/main.tf`
  with three production-correctness fixes applied (see commit history):
  account-id-suffixed bucket name for global uniqueness; `profile = "sandbox"`;
  `Currency=USD` dimension on billing alarms; `filter {}` on the lifecycle rule.
- `logs/` — one timestamped log per command (`NN_step_YYYYMMDD_HHMMSS.log`),
  each self-describing: command line, host, user, start/end, full stdout+stderr,
  exit code. Nothing trimmed.
- `evidence/plan_readable.txt` — human-readable `terraform show` of the plan.
- `evidence/plan.json` — machine-readable plan.
- `_runner.ps1` — the verbose-capture harness used to produce the logs.
- `run_preflight.ps1` — runs version/identity/init/validate/plan, each logged.

## What's intentionally NOT committed (see .gitignore)

- `.terraform/` provider binaries (hundreds of MB, transient)
- `terraform.tfstate*` (local state)
- `evidence/tfplan.binary` (binary plan; the readable + json renderings are kept)

## Run order

1. `run_preflight.ps1` — version, identity, init, validate, plan (read-only).
2. apply (gated on explicit human approval) — logged as `05_apply_*`.
3. live evidence capture via `aws` CLI (dashboard, resources) — logged.
4. `destroy` (gated on explicit human approval) — logged as `0N_destroy_*`.

Each step's log is committed so the entire run can be reconstructed from git
history alone.
