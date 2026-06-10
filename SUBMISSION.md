# ShadowDeploy — DoraHacks BUIDL Submission

> **AT-HAck0024 · AWS Prompt the Planet Challenge · Submission 08**
> **Well-Architected pillar:** Operational Excellence (with Reliability and Security)
> **In one line:** Mirrors a sampled slice of real production traffic to a new version, diffs outputs WITHOUT serving them, and reports divergence before promotion.

This document contains the three required BUIDL components plus a generated demo
evidence pack. Paste the prompt block into your AI coding tool; the rest is
supporting documentation for judges.

---

## Component 1 — The complete prompt (copy-paste ready)

```text
You are an AWS deployment-safety engineer. Build a shadow-testing harness that mirrors a sampled slice of real production traffic to a new service/model version, compares its outputs against production WITHOUT serving them to users, and reports diffs. Generate the IaC and comparison logic. Align to the AWS Well-Architected OPERATIONAL EXCELLENCE pillar (with Reliability) and call it out.

INPUT — Environment:
- Service type: [REST API / ML inference / async worker]
- Current prod entry point: [ALB / API Gateway — describe]
- New version to shadow: [container image / Lambda / model endpoint]
- Region: [e.g., us-east-1]
- IaC tool: [Terraform / CDK / CloudFormation]
- Sampling rate: [e.g., 5% of traffic]

REQUIREMENTS:
1. Mirror a sampled % of production requests to the shadow target (ALB traffic duplication / API Gateway + Lambda fan-out / VPC Traffic Mirroring as appropriate). Shadow responses are LOGGED, never returned to clients.
2. Capture prod and shadow responses with a correlation id; store to S3; diff with Athena (and optionally Bedrock to summarize semantic diffs for ML outputs).
3. Produce a comparison report: % matching, categorized differences, latency delta, error-rate delta.
4. Cost control: sampling cap, short log retention, and the ability to disable shadowing with one flag.
5. CloudWatch dashboard for shadow error rate and divergence.

OUTPUT FORMAT:
- IaC: mirroring config + shadow service + comparison storage + Athena diff + dashboard
- Comparison/diff Lambda source
- README: how to interpret the diff report and decide promotion
- Mermaid diagram of mirrored traffic flow

CRITICAL CONSTRAINTS:
- Shadow outputs MUST never reach end users — enforce architecturally (response discarded before client).
- HUMAN-IN-THE-LOOP: I review the diff report and explicitly approve promotion; the harness does not auto-promote.
- Mirroring doubles compute for sampled requests — print the added cost and keep sampling bounded.
- Tag everything; least-privilege; billing alerts at $10/$50/$100.

ADDITIONAL SUBMISSION-GRADE REQUIREMENTS:
- Before code, print an Assumptions table and ask for missing critical inputs only.
- Generate a Mermaid architecture diagram and AWS service responsibility table.
- Use least-privilege IAM, encryption at rest/in transit, resource tagging, and AWS Budgets alerts at $10/$50/$100.
- Provide exact sandbox test commands and expected output.
- Provide a demo artifact plan: screenshots/logs/dashboard/evidence pack required for DoraHacks submission.
- Do not auto-apply changes. Print IaC/apply commands separately and require explicit human approval.
- End with: cost estimate, security notes, rollback/disable plan, and Well-Architected pillar mapping.
```

> Scope note baked into the demo: bound the implementation to **one** pattern
> (API Gateway / Lambda REST) and a **fixed 5% sampling rate** to keep it
> hackathon-sized, as both reviewers advised.

---

## Component 2 — Context & docs

**Use case.** ML/backend teams shipping a new model or service version where
correctness is hard to unit-test and they want real-traffic validation before
promotion.

**Expected outcome.** A bounded shadow harness producing a prod-vs-shadow
comparison report (% match, categorized diffs, latency/error deltas) that
informs a human promotion decision. Shadow responses are never served.

**Prerequisites.** AWS account with CLI + credentials (use a dev/sandbox
account), an IaC tool (Terraform / CDK / CloudFormation), and an AI coding tool
(Kiro CLI, Claude Code, or Cursor).

**Troubleshooting.**
- *Shadow output reached a user* → mirroring misconfigured upstream; the harness
  discards shadow responses before the client by construction.
- *Cost spike* → lower sampling, shorten retention, or engage the one-flag
  kill-switch.
- *Everything flagged as a diff* → normalize non-deterministic fields
  (timestamps, request ids) before comparison.
- *No comparable pairs* → sampling produced no shadow captures; raise the rate
  or confirm shadowing is enabled.

---

## Component 3 — AWS services & best practices

**Services.** API Gateway / ALB (traffic mirroring), ECS / Lambda (shadow target
+ comparison), S3 + Athena (capture storage and diffing), CloudWatch (dashboard
+ alarms), optional Bedrock (semantic diff summaries for ML outputs), AWS
Budgets / CloudWatch billing (cost alarms).

**Well-Architected alignment.**
- **Operational Excellence (primary)** — small, reversible, evidence-based
  promotion; failure anticipated via pre-promotion divergence detection;
  human-in-the-loop operations.
- **Reliability** — shadow failures isolated from the production request path;
  candidate validated under real conditions.
- **Security** — PII masked at capture; S3 public-access blocked + encrypted;
  least-privilege IAM scoped to the capture bucket; bounded retention.
- **Cost Optimization** — sampling capped; cost surfaced up front; kill-switch;
  $10/$50/$100 billing alarms.

**Baked-in controls.** Shadow-discard guarantee (architectural), error isolation,
PII masking, deterministic sampling, billing alerts, resource tagging,
diff-before-apply (the prompt never auto-applies infrastructure).

---

## Component 4 — Demo evidence pack (generated, reproducible)

Generated by `scripts/generate_demo_evidence.py` against a realistic bounded
dataset: one day of `/v1/orders` traffic, 5% mirrored, where shadow **v2**
introduces a rounding change on ~2% of orders. The harness **caught it before
promotion** — which is the whole point.

### Promotion report (verdict: REVIEW)

| Metric | Value |
|---|---|
| Total compared | 171 |
| Matched | 168 |
| Match % | 98.25 |
| Mean prod latency (ms) | 12.81 |
| Mean shadow latency (ms) | 16.28 |
| Latency delta (ms) | 3.46 |
| Error-rate delta | 0.0 |
| Divergences | 3 × `changed` (the v2 rounding bug) |

**Verdict: REVIEW** — match 98.25% sits in the review band [95%, 99%). A human
reviews the 3 divergences and decides; the harness does not auto-promote.

### Shadow-discard guarantee — proven

The sample dataset stores shadow responses only for offline diffing; in
production they are discarded before the client. This is enforced structurally
in the mirror handler and covered by a dedicated functional test
(`test_client_always_gets_prod_response_even_when_shadow_differs`), which feeds a
deliberately-divergent shadow and asserts the client still receives prod.

### PII — masked at capture

Every captured body is PII-masked before persistence; the dataset contains
`***MASKED***` in place of customer emails, matching production behavior.

### Cost (at 5% sampling, scaled monthly)

Added cost ≈ **$0.07/month** at this volume — within the $100 budget, with
$10/$50/$100 billing alarms shipped in the IaC.

### Human approval record

`auto_promoted: false`. The v2 rounding divergence was identified before
promotion; shadow responses confirmed never served.

### KPI dashboard (CloudWatch `shadowdeploy-dev`)

- Shadow error rate: 0.0 (delta 0.0)
- Divergence rate: 1.75% of sampled pairs
- Latency delta: 3.46ms (shadow slower)
- Sampled volume: 171 requests/day at 5%

> Full artifacts: `demo_evidence/` — sample_dataset.json, diff_report.json/.md,
> execution_log.txt, human_approval.json, cost_report.json, kpi_dashboard.txt,
> evidence_manifest.json.

---

## Submission checklist

- [x] **The complete prompt**, verbatim and copy-paste ready.
- [x] **Context & docs** — prerequisites, use case, outcome, troubleshooting.
- [x] **AWS services & best practices** — services, Well-Architected alignment, controls.
- [x] **Bounded scope** — one API Gateway/Lambda pattern, fixed 5% sampling.
- [x] **Demo evidence pack** — diff report, % match, divergences, latency delta, shadow-discard confirmed, PII masked, human approval, cost.
- [x] **Submission-grade block** appended to the prompt.
- [ ] **Tested in Kiro/Claude Code on a real dev account** — *you must run this once on a sandbox; cannot be done offline.*
- [ ] **Final originality re-check on the live DoraHacks feed** — *check before the June 10 deadline; entries land late.*

**Winning-criteria self-check:**
- [x] Clear & actionable — concrete deliverable, intake-driven.
- [x] Production-ready — security, monitoring, cost controls, not hello-world.
- [x] Well-documented — intake, output format, troubleshooting present.
- [x] Well-Architected aligned — Operational Excellence named inside the prompt.

---

## Two items only you can close

1. **Run the prompt once in Kiro CLI or Claude Code against a dev/sandbox AWS
   account** to confirm it generates deployable output, then capture a live
   CloudWatch screenshot to replace the described dashboard. Everything else is
   done.
2. **Re-check originality on the live DoraHacks BUIDL feed** right before
   submitting — new entries land up to the deadline, and I can't see the live
   feed.
