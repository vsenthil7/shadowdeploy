# ShadowDeploy — Build Sprint Tracker

> Enterprise-grade reference implementation of the ShadowDeploy shadow-testing harness
> (AT-HAck0024 · AWS Prompt the Planet Challenge · Submission 08).
> No scope shrink. 100% test coverage targets: unit, functional, negative.

**Build start:** 2026-06-08 09:02
**Mode:** Continuous mini-sprints. Tracker updated at end of each sprint; no waiting between sprints.

---

## Definition of Done (applies to every sprint)

- Code written and importable, no syntax errors.
- Unit tests written for all new logic, passing.
- Negative tests for all failure/guard paths, passing.
- Functional tests where a flow spans modules, passing.
- Coverage for touched modules at 100% (line + branch where measurable).
- Tracker updated, then immediately proceed to next sprint.

---

## Sprint plan

| # | Sprint | Scope | Status |
|---|--------|-------|--------|
| 0 | Scaffold & tooling | Repo layout, packaging, pytest+coverage config, CI workflow | ✅ DONE |
| 1 | Core models & config | Typed domain models, config loader, sampling decision logic | ✅ DONE — 33 tests, 100% |
| 2 | Correlation & capture | Correlation IDs, request/response capture, PII masking | ✅ DONE — 25 tests, 100% |
| 3 | Normalization engine | Strip non-deterministic fields (timestamps, UUIDs, etc.) | ✅ DONE — 8 tests, 100% |
| 4 | Diff engine | Structural + semantic-ready diff, categorized divergences | ✅ DONE — 15 tests, 100% |
| 5 | Metrics & deltas | Match %, latency delta, error-rate delta, aggregation | ✅ DONE — 4 tests, 100% |
| 6 | Lambda handlers | Mirror fan-out, capture, comparison handlers | ✅ DONE — 11 tests, 100% |
| 7 | Reporting | Diff report builder, promotion verdict, JSON + Markdown | ✅ DONE — 10 tests, 100% |
| 8 | Cost governance | Cost estimator, sampling cap, kill-switch flag | ✅ DONE — 9 tests, 100% |
| 9 | IaC generation | Terraform + CDK emitters for the harness | ✅ DONE — 13 tests, 100% |
| 10 | CLI & orchestration | Entry point wiring it all together | ✅ DONE — 12 tests, 100% |
| 11 | Docs (market-standard) | README, ARCHITECTURE, SECURITY, etc. in docs/ | ✅ DONE — 7 docs + license |
| 12 | Full test sweep & coverage gate | Run all suites, enforce 100%, finalize | ✅ DONE — 140 tests, 100% gate |

---

## Sprint log

### Sprint 0 — Scaffold & tooling — ✅ DONE
- Repo directory structure created.
- pyproject.toml, pytest.ini, .coveragerc, CI workflow.
- Verified Python 3.12 / Node 22 available.

### Sprint 1 — Core models & config — ✅ DONE
- `core/models.py`: ServiceType, MirrorConfig, CapturedExchange, DiffResult, etc.
- `core/config.py`: validated config loader with bounds enforcement.
- `core/sampling.py`: deterministic + probabilistic sampling decision.
- Tests: unit + negative for bounds, invalid enums, sampling determinism.

### Sprint 2 — Correlation & capture — ✅ DONE
- `core/correlation.py`: correlation ID generation/propagation.
- `core/capture.py`: exchange capture with PII masking hooks.
- `core/pii.py`: PII masking (email, phone, SSN, card, token).
- Tests: masking correctness, idempotency, negative malformed input.

### Sprint 3 — Normalization engine — ✅ DONE
- `core/normalize.py`: configurable non-deterministic field stripping.
- Tests: timestamp/uuid/random normalization, nested structures, negatives.

### Sprint 4 — Diff engine — ✅ DONE
- `core/diff.py`: recursive structural diff, categorized (added/removed/changed/type).
- Tests: deep nesting, lists, type mismatches, negatives.

### Sprint 5 — Metrics & deltas — ✅ DONE
- `core/metrics.py`: match %, latency/error deltas, aggregation across batch.
- Tests: aggregation math, empty batch guard, negatives.

### Sprint 6 — Lambda handlers — ✅ DONE
- `handlers/mirror.py`, `handlers/capture_handler.py`, `handlers/compare_handler.py`.
- Shadow response discard guarantee enforced + tested.
- Tests: fan-out, discard guarantee, error isolation, negatives.

### Sprint 7 — Reporting — ✅ DONE
- `reporting/report.py`: report builder, promotion verdict logic.
- `reporting/render.py`: JSON + Markdown renderers.
- Tests: verdict thresholds, rendering, negatives.

### Sprint 8 — Cost governance — ✅ DONE
- `core/cost.py`: cost estimator, sampling cap enforcement, kill-switch.
- Tests: cost math, cap enforcement, kill-switch, negatives.

### Sprint 9 — IaC generation — ✅ DONE
- `iac/terraform_emitter.py`, `iac/cdk_emitter.py`.
- Tests: emitted-config validity, tagging, least-priv presence, negatives.

### Sprint 10 — CLI & orchestration — ✅ DONE
- `cli.py`: orchestrates config→sample→capture→diff→report.
- Tests: end-to-end functional run, negatives.

### Sprint 11 — Docs — ✅ DONE
- docs/: README, ARCHITECTURE, SECURITY, CONTRIBUTING, etc.

### Sprint 12 — Full test sweep — ✅ DONE
- All suites green, coverage at 100%.


---

## Final build summary (2026-06-08)

**All 12 sprints complete. No scope shrink.**

- **Tests:** 140 total — 95 unit, 13 functional, 32 negative (markers overlap).
- **Coverage:** 100% line and 100% branch across all 23 source modules
  (572 statements, 144 branches, 0 missed). CI gate `--cov-fail-under=100` passes.
- **Safety invariants under test:** shadow-discard guarantee, shadow error
  isolation, PII masking, diff-noise normalization, error-rate BLOCK verdict.
- **Deliverables:** Python package (core/handlers/reporting/iac), CLI (3
  subcommands), Terraform + CDK emitters, 7 market-standard docs + LICENSE,
  example config + captures fixtures, GitHub Actions CI workflow.
- **Validation:** CLI exercised end-to-end on example fixtures; docs verified
  accurate against real output.


---

## Post-build: submission package (2026-06-08, added after sprints)

**Demo evidence pack + submission document — DONE.**

- Added `scripts/generate_demo_evidence.py` — bounded demo (one API Gateway/Lambda
  REST pattern, fixed 5% sampling). Produces sample dataset, diff report (JSON+MD),
  execution log, human-approval record, cost report, KPI dashboard, manifest.
- Demo deliberately includes a shadow-v2 rounding divergence on ~2% of orders so
  the report shows a realistic **REVIEW** verdict (98.25% match) — proving the
  harness catches a real defect before promotion.
- **Bug found and fixed during demo build:** initial demo constructed captures
  directly, bypassing PII masking, which leaked (fake) emails into the dataset.
  Fixed to route through `capture_exchange`; dataset now fully masked. Lesson:
  always use the real capture path.
- Added 7 demo tests; full suite now **147 tests, 100% coverage** (scripts included
  in the gate).
- Wrote `SUBMISSION.md` — the three required BUIDL components + demo evidence,
  checklist ticked.

**Two items only the user can close (cannot be done offline):**
1. Run the prompt once in Kiro/Claude Code on a dev/sandbox account; capture a
   live CloudWatch screenshot.
2. Final originality re-check on the live DoraHacks feed before the June 10 deadline.
