# Contributing

## Development workflow

1. `pip install -e ".[dev]"`
2. Write the code and its tests together. New logic ships with:
   - unit tests covering every branch,
   - a negative test for every guard/`raise`,
   - a functional test if the change spans modules.
3. Run the full gate locally: `pytest --cov=shadowdeploy --cov-branch --cov-fail-under=100`.
4. Keep modules dependency-free (stdlib only) so they run in a Lambda runtime.

## Standards

- Type hints on public functions; frozen dataclasses for models.
- Validation lives in `core/config.py`; models stay pure data.
- No cloud calls in library code — IaC emitters produce text, never apply.
- The shadow-discard guarantee and error isolation are invariants; any change to
  `handlers/mirror.py` must keep their functional tests passing.

## Commit hygiene

- One logical change per commit.
- Reference the sprint or module touched.
- CI must be green (100% coverage gate) before merge.
