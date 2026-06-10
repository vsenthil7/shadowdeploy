# Testing

ShadowDeploy enforces **100% line and branch coverage** across three test
categories. The CI gate fails the build below 100%.

## Categories

- **Unit** (`tests/unit/`) — every module's logic in isolation, including all
  branches and guard clauses.
- **Functional** (`tests/functional/`) — flows that span modules: the mirror
  handler's discard guarantee, the compare batch, the orchestrator pipeline, and
  the CLI end-to-end on fixtures.
- **Negative** — failure paths and guards. These are marked with
  `@pytest.mark.negative` and live alongside the unit/functional tests they
  relate to, so each guard is tested next to the code it protects.

Markers are declared in `pyproject.toml` (`unit`, `functional`, `negative`).

## Running

```bash
# Everything, with the 100% gate
pytest --cov=shadowdeploy --cov-branch --cov-report=term-missing --cov-fail-under=100

# Just one category
pytest -m negative
pytest -m functional
pytest -m unit
```

## What "100%" covers here

- Every statement executes.
- Every branch (both sides of each `if`, each loop entry/skip) executes.
- Every raised `ValueError` guard has a negative test that triggers it.
- The critical safety properties have dedicated functional tests:
  - client always receives the prod response (discard guarantee),
  - shadow errors are isolated from the client,
  - normalization removes non-deterministic diff noise,
  - the verdict blocks on error-rate regression.

## Coverage exclusions

Only two lines are excluded, both standard and non-logical:
`if __name__ == "__main__":` shims and a defensive `pragma: no cover` branch in
`compare_handler.pair_captures` that `capture_exchange` already makes
unreachable (an unknown capture source). These are documented inline.

## Adding tests

New logic must ship with unit tests for its branches and a negative test for
each guard before it merges. See [CONTRIBUTING.md](CONTRIBUTING.md).
