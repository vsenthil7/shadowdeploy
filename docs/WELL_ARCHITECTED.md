# AWS Well-Architected Alignment

ShadowDeploy's primary pillar is **Operational Excellence**, with strong
**Reliability** and **Security** contributions.

## Operational Excellence (primary)

- **Make frequent, small, reversible changes.** Shadow testing lets a new
  version prove itself against real traffic before promotion, making the change
  safer and the decision evidence-based.
- **Anticipate failure.** The comparison report surfaces divergence and
  error-rate regression *before* the change is promoted.
- **Learn from operational events.** Every run produces a stored, queryable
  record of how the candidate behaved on production traffic.
- **Human-in-the-loop operations.** Promotion is a human decision informed by a
  verdict, never automated.

## Reliability

- **Test recovery procedures / validate behavior under real conditions.** The
  harness exercises the candidate on genuine production request shapes.
- **Stop guessing capacity / fail isolation.** Shadow failures are isolated from
  the production path so testing never reduces availability.

## Security

- **Apply security at all layers.** PII masking at capture, S3 public-access
  blocks, encryption at rest, least-privilege IAM scoped to the capture bucket.
- **Protect data in transit and at rest.** Captures are encrypted; retention is
  bounded by lifecycle expiry.
- **Prepare for security events.** No unmasked PII is ever persisted, limiting
  blast radius if the capture store is compromised.

## Cost Optimization

- **Adopt a consumption model / stop sampling more than you need.** Sampling is
  capped at config load; cost is estimated up front; a kill-switch and
  $10/$50/$100 billing alarms bound spend.

## Performance Efficiency

- **Go global / use serverless.** The reference IaC favors serverless capture
  and out-of-band comparison so the inline request path stays lean — only a
  bounded sample incurs the extra shadow invocation.

## Sustainability

- **Maximize utilization / minimize waste.** Bounded sampling and short
  retention mean the harness stores and processes only what the promotion
  decision requires.
