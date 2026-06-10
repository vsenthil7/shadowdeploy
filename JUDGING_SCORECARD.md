# ShadowDeploy — Judging Criteria Scorecard

> Honest self-assessment against the AT-HAck0024 official judging criteria,
> prepared 2026-06-08 before external review by ChatGPT and Perplexity.
> Scored conservatively. Where a point depends on something only the user can do
> (live deploy), it is marked as a gap, not assumed.

---

## Source of criteria

From the challenge Assessment (Component requirements + Winning criteria):

**BUIDL completeness (must have all three):**
1. The complete prompt — verbatim, copy-paste ready.
2. Context & docs — prerequisites, use case, expected outcome, troubleshooting.
3. AWS services & best practices — services used, Well-Architected alignment,
   security/cost/operational principles.

**Winning criteria (the 4 the judges score on):**
- A. Clear & actionable
- B. Production-ready (security, monitoring, cost controls — not hello-world)
- C. Well-documented
- D. Aligned with AWS Well-Architected Framework

**Implied / reviewer-added:** demonstrable proof (demo evidence pack);
originality vs the existing field; tooling fit (Kiro/Claude Code).

---

## Scorecard

### BUIDL completeness (gate — must be 100% or it's incomplete)

| Requirement | Status | Evidence |
|---|---|---|
| Complete prompt, copy-paste ready | ✅ | `SUBMISSION.md` Component 1, fenced block, all intake placeholders present |
| Context & docs | ✅ | Component 2 — prerequisites, use case, outcome, troubleshooting all present |
| AWS services & best practices | ✅ | Component 3 — services list + Well-Architected mapping + baked-in controls |

**Completeness: 3/3 = 100%.** The submission is *complete* as a BUIDL.

---

### Winning criteria (weighted quality score)

#### A. Clear & actionable — 9.0 / 10
- Intake table with typed placeholders; the model knows exactly what to ask.
- Concrete deliverables named (IaC, diff Lambda, README, Mermaid).
- One unambiguous job: mirror, diff, report, don't serve.
- *Minor gap:* the prompt offers three mirroring mechanisms (ALB dup / API GW
  fan-out / VPC mirroring) and says "as appropriate" — slight ambiguity the
  model must resolve. Bounded in the demo to one pattern, but the prompt itself
  keeps the choice open. -1.0.

#### B. Production-ready — 9.0 / 10
- Security: least-privilege IAM, encryption, tagging, PII masking (proven in the
  reference impl).
- Monitoring: CloudWatch dashboard for error rate + divergence.
- Cost: sampling cap, short retention, one-flag kill-switch, $10/$50/$100 alarms.
- Safety: shadow-discard guarantee enforced architecturally; human-in-the-loop;
  no auto-apply.
- *Gap:* "production-ready" is asserted in the prompt and demonstrated in the
  reference implementation, but **the prompt's own generated output has not been
  run on a live AWS dev account yet** — so production-readiness of what the
  prompt *generates* is validated by the reference build, not by an actual Kiro
  run. -1.0.

#### C. Well-documented — 9.5 / 10
- Intake, output format, troubleshooting, expected outcome all present.
- Supporting repo has ARCHITECTURE, SECURITY, TESTING, RUNBOOK, WELL_ARCHITECTED.
- Demo evidence pack documents an actual run end-to-end.
- *Minor:* docs live in the supporting repo; a judge reading only the BUIDL text
  sees the essentials but not the full set. -0.5.

#### D. Well-Architected aligned — 9.5 / 10
- Operational Excellence named explicitly inside the prompt (criterion the
  reviewers specifically flagged).
- Reliability, Security, Cost Optimization all mapped in Component 3 and the repo
  doc.
- *Minor:* Performance Efficiency / Sustainability touched only lightly. -0.5.

**Winning-criteria average: (9.0 + 9.0 + 9.5 + 9.5) / 4 = 9.25 / 10 = 92.5%.**

---

### Differentiators (not scored directly, but judges weigh them)

| Factor | Status |
|---|---|
| Originality vs field | Strong — both reviewers noted "almost no competition" for shadow-testing; mirror-and-diff with never-served responses is a clean, rare angle. Pending final live-feed re-check. |
| Demonstrable proof | ✅ Demo evidence pack now exists; shows a real defect caught (REVIEW @ 98.25%). |
| Proof-gated framing | ✅ Discard guarantee is architectural + functionally tested, matching the "proof-gated" theme that scored highest in the field. |
| Tooling fit | ✅ Prompt is Kiro/Claude Code/Cursor agnostic; intake-driven. |

---

## Overall readiness

| Dimension | Score |
|---|---|
| BUIDL completeness (gate) | 100% (3/3) |
| Winning-criteria quality | 92.5% |
| **Match to judge requirements (blended)** | **~92%** |

### What the ~8% gap is made of

The score is held back almost entirely by **one thing I cannot do from here**:
the prompt has not been executed in Kiro CLI / Claude Code against a live AWS
dev account. That single live run would:
- confirm the prompt generates deployable IaC (lifts B toward 10),
- yield a real CloudWatch screenshot to replace the described dashboard,
- let you tick the last open checklist item.

The only other deductions are minor (mechanism ambiguity in the prompt; docs
living in the repo vs inline). None are blocking.

### Verdict

**Ready for peer review (ChatGPT / Perplexity): yes.**
**Ready for final DoraHacks submission: after one live Kiro run + originality
re-check.** Everything that can be done offline is done and verified at 100% on
the engineering side.

---

## V2 re-score (after closing the fixable deductions)

`PROMPT_V2.md` closes the two open items that were in my control:

- **Criterion A (Clear & actionable): 9.0 -> 9.5.** STEP 0 now forces exactly one
  mirroring mechanism via an explicit decision rule, removing the "as
  appropriate" ambiguity. (-0.5 remains: any rich prompt leaves *some* judgment
  to the model.)
- **Criterion B (Production-ready): 9.0 -> 9.5.** PII masking, normalization,
  error isolation, and a hard sampling cap are now explicit *in the prompt*, not
  just in the reference impl. (-0.5 remains until a live Kiro run validates the
  generated output.)
- **Criterion C: 9.5** (unchanged).
- **Criterion D: 9.5** (unchanged).
- **New strength:** canary metrics requirement (#5) directly implements
  ChatGPT's prioritised prompt-specific upgrade.

**V2 winning-criteria average: (9.5 + 9.5 + 9.5 + 9.5) / 4 = 9.5 / 10 = 95%.**

| Dimension | V1 | V2 |
|---|---|---|
| BUIDL completeness (gate) | 100% | 100% |
| Winning-criteria quality | 92.5% | 95% |
| **Blended match to judge requirements** | **~92%** | **~95%** |

The remaining ~5% is the live Kiro/Claude Code run on a dev account (cannot be
done offline) plus the irreducible "model still makes some choices" residue and
the final live-feed originality check. No further offline change moves the
number materially — the next gain comes from the live run, which is yours to do.
