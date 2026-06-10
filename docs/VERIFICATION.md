# Local Verification Record — ShadowDeploy

This file records test runs actually executed on a developer machine, so that
claims of "100% coverage / all tests pass" in commit messages trace to captured
output rather than assertion.

## Run 1 — Windows / Python 3.12.10

- **Date:** 2026-06-10
- **Host OS:** Windows 11 (AMD64)
- **Python:** 3.12.10 (CPython)
- **Environment:** local `.venv`, package installed via `pip install -e ".[dev]"`
- **Command:**
  ```
  pytest --cov=shadowdeploy --cov=scripts --cov-branch --cov-report=term-missing --cov-fail-under=100
  ```
- **Result:** `147 passed in 1.28s`
- **Coverage:** TOTAL 650 statements, 0 missed; 150 branches, 0 partial. **100.00%** line and branch.
- **Gate:** `--cov-fail-under=100` satisfied.

All 25 source modules under `src/shadowdeploy/` and `scripts/` reported 100%
line and branch coverage with zero missing lines.

> This is the offline test suite (deterministic, no AWS calls). It validates the
> reference implementation. It does NOT validate a live AWS deployment — that is
> a separate step (running PROMPT_V2 via Kiro against a sandbox account) and is
> tracked separately, not claimed here.
