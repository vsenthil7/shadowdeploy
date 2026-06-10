# Security

## Threat model

ShadowDeploy sits in the production request path, so its security posture
matters as much as the services it tests. The main risks and mitigations:

| Risk | Mitigation |
|---|---|
| Shadow response leaks to a client | Structural discard guarantee in the mirror handler; client response bound before shadow runs; covered by a functional test. |
| Shadow failure degrades production | Shadow invocation wrapped in try/except; errors logged, never propagated to the client path. |
| Captured bodies become a PII store | All bodies masked (`core/pii.py`) before persistence: email, SSN, card, phone, bearer tokens, plus caller-named fields. |
| Capture bucket exposed | IaC sets `BlockPublicAccess.BLOCK_ALL` / all four S3 public-access blocks; bucket encrypted; lifecycle expiry bounds retention. |
| Over-broad IAM | Comparison role granted only `s3:GetObject` / `s3:PutObject` scoped to the capture bucket ARN — no wildcards. Asserted in IaC tests. |
| Runaway cost as a denial-of-wallet vector | Sampling capped at 0.25 at config load; cost estimator surfaces spend; one-flag kill-switch; billing alarms at $10/$50/$100. |

## PII handling

Masking is applied at capture time, in-process, before any write. Two layers:

1. **Pattern masking** of string values: email addresses, US SSNs, 13–16 digit
   card numbers, bearer tokens, and phone numbers.
2. **Named-field masking**: any dict key listed in `pii_fields` is fully masked
   regardless of value type (e.g. `password`, `ssn`).

Masking is recursive across nested dicts and lists. See
`tests/unit/test_sprint2_capture.py` for the coverage.

## IAM posture

- Least-privilege role per function; comparison role scoped to the capture
  bucket only.
- No long-lived keys in the harness; roles assumed by the Lambda service
  principal.
- Generated IaC is reviewed by a human (diff-before-apply) — the CLI emits text;
  it never applies infrastructure.

## Data retention

Captures expire via an S3 lifecycle rule. Retention is bounded at config load
(1–30 days) so the diff store cannot grow without limit.

## Reporting a vulnerability

This is a hackathon reference implementation. For the challenge submission,
report issues via the DoraHacks BUIDL page. In a production fork, route through
your organization's security disclosure process.
