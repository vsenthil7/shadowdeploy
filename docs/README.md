# ShadowDeploy

> Bounded shadow-testing harness that mirrors a sampled slice of real production
> traffic to a new version, diffs the outputs **without ever serving them**, and
> reports divergence before promotion.

**AT-HAck0024 · AWS Prompt the Planet Challenge · Submission 08**
**Primary AWS Well-Architected pillar:** Operational Excellence (with Reliability and Security).

---

## What this is

ShadowDeploy lets you validate a new service or model version against *real*
production traffic without risk: a sampled percentage of live requests is
mirrored to the shadow target, both responses are captured and compared, and a
promotion verdict (PROMOTE / REVIEW / BLOCK) is produced for a human to act on.
The shadow response is **discarded before it can reach a client** — that
guarantee is enforced structurally in the mirror handler, not by convention.

This repository contains an enterprise-grade reference implementation of the
harness the ShadowDeploy prompt generates: the comparison logic, handlers, cost
governance, reporting, and Infrastructure-as-Code emitters, with 100% test
coverage across unit, functional, and negative suites.

## Key properties

- **Shadow-discard guarantee.** The client always receives the production
  response. The shadow result is captured for diffing then dropped. See
  `handlers/mirror.py` and `tests/functional/test_sprint6_handlers.py`.
- **Error isolation.** A failure in the shadow path never affects the client.
- **PII-safe captures.** Bodies are masked (email, SSN, card, phone, bearer
  tokens, and caller-named fields) before anything is persisted.
- **Noise-free diffs.** Timestamps, UUIDs, and epochs are normalized so the diff
  surfaces real divergence, not non-determinism.
- **Bounded cost.** Sampling is capped at config-load time; the cost estimator
  prints the added spend; a one-flag kill-switch disables shadowing instantly;
  billing alarms at $10 / $50 / $100 ship in the IaC.
- **Human-in-the-loop.** The verdict is advisory. The harness never auto-promotes.

## Quick start

```bash
pip install -e ".[dev]"

# Generate Terraform for the harness
shadowdeploy emit-iac --config examples/config.json --environment dev

# Estimate the added monthly cost at 1M requests
shadowdeploy estimate --config examples/config.json --monthly-requests 1000000

# Build a promotion report from recorded captures
shadowdeploy report --config examples/config.json --captures examples/captures.json --format markdown
```

## Repository layout

```
src/shadowdeploy/
  core/         models, config, sampling, correlation, capture, pii,
                normalize, diff, metrics, cost
  handlers/     mirror (discard guarantee), compare_handler
  reporting/    report (verdict), render (json/markdown)
  iac/          terraform_emitter, cdk_emitter
  orchestrator.py   in-process pipeline
  cli.py            command-line entry point
tests/
  unit/         per-module unit + negative tests
  functional/   cross-module flows (handlers, orchestrator, CLI)
  negative/     shared failure-path checks
docs/           this documentation set
infra/          terraform + cdk scaffolding
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — components, data flow, the discard guarantee.
- [SECURITY.md](SECURITY.md) — threat model, PII handling, IAM posture.
- [TESTING.md](TESTING.md) — test strategy and how coverage is enforced.
- [RUNBOOK.md](RUNBOOK.md) — operating the harness, kill-switch, incident steps.
- [WELL_ARCHITECTED.md](WELL_ARCHITECTED.md) — pillar-by-pillar alignment.
- [CONTRIBUTING.md](CONTRIBUTING.md) — dev workflow and standards.
- [CHANGELOG.md](CHANGELOG.md) — version history.

## License

MIT. See [LICENSE](../LICENSE).
