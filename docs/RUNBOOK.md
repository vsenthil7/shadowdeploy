# Runbook

Operational procedures for running the ShadowDeploy harness.

## Deploy

1. Author a config JSON (see `examples/config.json`).
2. Generate IaC: `shadowdeploy emit-iac --config config.json --environment dev`.
3. **Review the generated plan and cost estimate** before applying anything.
   Treat it like a junior engineer's pull request — hand-check IAM, security
   groups, and sizing.
4. Apply to a **dev/sandbox account first**, never straight to production.
5. Estimate cost: `shadowdeploy estimate --config config.json --monthly-requests <N>`.
6. Monitor cost and the CloudWatch dashboard for **≥48 hours** before promoting.

## Interpreting a promotion report

Run `shadowdeploy report --config config.json --captures captures.json`.

| Verdict | Meaning | Action |
|---|---|---|
| PROMOTE | Match % above threshold, no error/latency regression. | Human approves promotion. |
| REVIEW | Match in the review band, or latency regressed. | Inspect divergences before deciding. |
| BLOCK | Match below threshold, or shadow raised the error rate. | Do not promote; investigate. |

The verdict is advisory. **A human always approves promotion** — the harness
never auto-promotes.

## Kill-switch (disable shadowing immediately)

Set `shadow_enabled: false` in the config and redeploy the mirror, or flip the
`shadow_enabled` local/output in the generated IaC. With it off:

- no requests are mirrored,
- the cost estimate drops to zero added cost,
- `kill_switch_active(config)` returns `True`.

Use this if costs spike or a shadow defect risks the request path.

## Common incidents

| Symptom | Likely cause | Fix |
|---|---|---|
| A shadow response reached a user | Mirroring misconfigured upstream | Confirm the mirror handler is in the path and the shadow edge is duplication-only; the handler itself cannot serve shadow output. |
| Cost spike | Sampling too high / retention too long | Lower `sampling_rate`, shorten `log_retention_days`, or engage the kill-switch. |
| Everything flagged as a diff | Non-deterministic fields not normalized | Add the offending keys to `ignore_fields`; confirm timestamps/UUIDs are covered by `normalize`. |
| No comparable pairs in the report | Sampling produced no shadow captures | Raise `sampling_rate` or confirm `shadow_enabled` is true. |

## Health signals

- **Shadow error rate** (CloudWatch) — rising means the new version is failing
  on real traffic.
- **Divergence rate** (CloudWatch) — rising means behavior is drifting from prod.
- **Latency delta** (report) — shadow slower than prod beyond tolerance triggers
  a REVIEW downgrade.
