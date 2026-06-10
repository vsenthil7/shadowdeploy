# Changelog

All notable changes to this project are documented here. Format based on
Keep a Changelog; this project adheres to semantic versioning.

## [1.0.0] - 2026-06-08

### Added
- Core domain models, validated config loader, deterministic sampling.
- Correlation id handling, PII-masking capture, non-determinism normalization.
- Recursive categorized diff engine and batch metrics aggregation.
- Mirror handler with structural shadow-discard guarantee and error isolation.
- Compare handler (pair + normalize + diff a batch).
- Promotion report with PROMOTE/REVIEW/BLOCK verdict; JSON + Markdown renderers.
- Cost governance: estimator, budget check, kill-switch, billing-alert thresholds.
- Terraform and CDK IaC emitters with tagging, least-privilege IAM, public-access
  blocks, lifecycle retention, and billing alarms.
- In-process orchestrator pipeline and a three-subcommand CLI.
- Full test suite: unit, functional, and negative, at 100% line and branch coverage.
- Documentation set: README, ARCHITECTURE, SECURITY, TESTING, RUNBOOK,
  WELL_ARCHITECTED, CONTRIBUTING.
