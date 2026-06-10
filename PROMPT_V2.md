# ShadowDeploy — Prompt V2 (review-ready)

> This is the tightened prompt addressing the two open items from prior reviews:
> (1) mechanism ambiguity in V1 (criterion A deduction), and (2) ChatGPT's
> prioritised prompt-specific upgrade: canary deployment metrics alongside the
> shadow diff. Use this block for the ChatGPT/Perplexity review pass.

```text
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

## What changed from V1 and why

| Change | Closes | Reviewer source |
|---|---|---|
| STEP 0 decision rule forces ONE mirroring mechanism | Criterion A ambiguity (-1.0 in scorecard) | self-scorecard |
| Canary metrics requirement (#5) | "Canary deployment metrics alongside the shadow diff — prioritise" | ChatGPT prompt-specific upgrade |
| Explicit PII masking + normalization steps | makes baked-in safety visible in the prompt itself | matches reference impl |
| Verdict (PROMOTE/REVIEW/BLOCK) named in #4 | aligns prompt output with the demo evidence | self |
| Error isolation made an explicit constraint | hardens the safety story | self |
| Sampling hard cap stated (25%) | bounds scope-creep risk reviewers flagged | both reviewers |

## Deliberately NOT added

- **Rollback confidence engine** (ChatGPT, optional): the human promotion gate +
  the BLOCK verdict already cover the decision. Adding a rollback engine widens
  scope past hackathon size — both reviewers warned against scope creep. Left out
  on purpose; note this when reviewing.
- **The full V02 judging-grade layer** (business KPIs, executive views, override
  matrix, production-readiness /100): available in the source file as an optional
  append. Not folded into the core prompt to keep it tight and copy-paste usable;
  attach separately if a judge wants the enterprise framing.
