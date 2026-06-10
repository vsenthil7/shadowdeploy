# ShadowDeploy

**Mirror a sampled slice of real production traffic to a new version, diff the outputs against production *without ever serving them to users*, and report divergence with a PROMOTE / REVIEW / BLOCK verdict — so a human catches defects before they reach customers.**

AWS Well-Architected pillar: **Operational Excellence** (with Reliability and Security).

---

## Component 1 — The complete prompt (copy-paste ready)

```
You are an AWS deployment-safety engineer. Build a shadow-testing harness that mirrors a sampled slice of real production traffic to a new service/model version, compares its outputs against production WITHOUT serving them to users, and reports divergence so a human can decide promotion. Generate the IaC and comparison logic. Align explicitly to the AWS Well-Architected OPERATIONAL EXCELLENCE pillar (with Reliability and Security) and name it in your output.

STEP 0 — Before any code:
- Print an Assumptions table.
- Ask ONLY for missing critical inputs from the INPUT block below.
- Pick exactly ONE mirroring mechanism using this decision rule, and state which and why:
    * API Gateway REST/HTTP prod entry point  -> API Gateway + Lambda fan-out (DEFAULT).
    * ALB in front of ECS/EC2                 -> ALB request mirroring.
    * Raw TCP/UDP or non-HTTP                  -> VPC Traffic Mirroring.
  Do not implement more than one mechanism.

INPUT — Environment:
- Service type: [REST API / ML inference / async worker]
- Current prod entry point: [ALB / API Gateway — describe]
- New version to shadow: [container image / Lambda / model endpoint]
- Region: [e.g., us-east-1]
- IaC tool: [Terraform / CDK / CloudFormation]
- Sampling rate: [default 5% of traffic; hard cap 25%]

REQUIREMENTS:
1. Mirror the chosen sampled % of production requests to the shadow target via the ONE selected mechanism. Shadow responses are LOGGED, never returned to clients.
2. Capture prod and shadow responses with a shared correlation id; mask PII at capture (email, phone, SSN, card, bearer tokens, and any caller-named fields) BEFORE persistence; store to S3 with short retention. Diff with Athena (optionally Bedrock to summarize semantic diffs for ML outputs).
3. Normalize non-deterministic fields (timestamps, UUIDs, request ids) before diffing so only meaningful divergence is reported.
4. Produce a comparison report: % matching, categorized differences (added/removed/changed/type-mismatch), latency delta, error-rate delta, and a PROMOTE / REVIEW / BLOCK verdict against stated thresholds.
5. CANARY METRICS: alongside the shadow diff, emit the canary signals a human needs for the promotion call — shadow error rate vs prod, p50/p95 latency delta, divergence rate trend over the sample window, and a single recommended action. The verdict must BLOCK on an error-rate regression beyond tolerance.
6. Cost control: sampling cap, short log retention, and a one-flag kill-switch that disables shadowing immediately.
7. CloudWatch dashboard for shadow error rate and divergence.

OUTPUT FORMAT:
- Assumptions table + chosen mirroring mechanism (with reason).
- IaC: mirroring config + shadow service + comparison storage + Athena diff + dashboard.
- Comparison/diff Lambda source.
- Mermaid architecture diagram of mirrored traffic flow + an AWS service responsibility table.
- README: how to interpret the diff + canary report and decide promotion.
- Exact sandbox test commands and expected output.
- End with: cost estimate, security notes, rollback/disable plan, and Well-Architected pillar mapping.

CRITICAL CONSTRAINTS:
- Shadow outputs MUST never reach end users — enforce architecturally (response discarded before the client path returns, not by convention).
- A shadow failure MUST be isolated — it can never affect the production response.
- HUMAN-IN-THE-LOOP: the harness presents the verdict + canary metrics; I review and explicitly approve promotion. It does not auto-promote.
- Mirroring doubles compute for sampled requests — print the added cost and keep sampling bounded (cap 25%).
- Tag every resource; least-privilege IAM scoped to named resources (no wildcards); encryption at rest/in transit; AWS Budgets alerts at $10/$50/$100.
- Do not auto-apply changes. Print IaC/apply commands separately and require explicit human approval.
```

---

## Component 2 — Context & docs

**Use case.** ML and backend teams shipping a new model or service version where correctness is hard to unit-test, who want validation against *real* traffic before promoting — without risking a single user seeing an unverified response.

**Expected outcome.** A bounded shadow harness that produces a prod-vs-shadow comparison report (% match, categorized diffs, latency and error-rate deltas) plus canary signals, ending in a PROMOTE / REVIEW / BLOCK verdict that informs a human promotion decision. Shadow responses are never served.

**Prerequisites.** An AWS account with CLI + credentials (use a dev/sandbox account), an IaC tool (Terraform / CDK / CloudFormation), and an AI coding tool (Kiro CLI, Claude Code, or Cursor).

**Troubleshooting.**
- *A shadow response reached a user* — mirroring is misconfigured upstream; the harness discards shadow responses before the client path returns, by construction.
- *Cost spike* — lower the sampling rate, shorten retention, or engage the one-flag kill-switch.
- *Everything flagged as a diff* — non-deterministic fields aren't normalized; confirm timestamps, UUIDs and request ids are in the normalization list.
- *No comparable pairs* — sampling produced no shadow captures; raise the rate or confirm shadowing is enabled.

---

## Component 3 — AWS services & best practices

**Services.** API Gateway / ALB (traffic mirroring), Lambda / ECS (shadow target + comparison), S3 + Athena (capture storage and diffing), CloudWatch (dashboard + alarms), optional Bedrock (semantic diff summaries for ML outputs), AWS Budgets / CloudWatch billing (cost alerts).

**Well-Architected alignment.**
- **Operational Excellence (primary)** — small, reversible, evidence-based promotion; failure anticipated via pre-promotion divergence detection; human-in-the-loop operations.
- **Reliability** — shadow failures are isolated from the production request path; the candidate is validated under real conditions before promotion.
- **Security** — PII masked at capture; S3 public access blocked and encrypted; least-privilege IAM scoped to named resources (no wildcards); bounded retention.
- **Cost Optimization** — sampling capped (hard cap 25%); added cost surfaced up front; one-flag kill-switch; billing alarms at $10 / $50 / $100.

**Baked-in controls.** Architectural shadow-discard guarantee, shadow-failure isolation, PII masking, deterministic sampling, response normalization, billing alerts, resource tagging, and diff-before-apply (the prompt never auto-applies infrastructure).

---

## Proof

This prompt is backed by a full reference implementation (Python, Terraform + CDK IaC) with **147 tests at 100% line and branch coverage**, and the generated infrastructure was **deployed to a live AWS account and verified**: a real CloudWatch dashboard, S3 capture bucket with all public access blocked and a 7-day retention lifecycle, and billing alarms at $10/$50/$100 — then torn down. Every command and its output is captured in the repository.

**Repository (impl, tests, IaC, live-run logs + screenshots):** https://github.com/vsenthil7/shadowdeploy
