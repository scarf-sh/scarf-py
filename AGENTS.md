# Scarf Python SDK – Agent Notes

This document distills the pieces of the repository that typically matter during short agent
engagements. Use it as a fast orientation guide before you dive into tasks.

## Repository Map

- `scarf/event_logger.py` – core client. Exposes `ScarfEventLogger`, manages the shared
  `requests.Session`, builds an extended `User-Agent`, and centralises timeout + verbose handling.
- `scarf/version.py` – computes `__version__` by reading `pyproject.toml`, with a runtime fallback
  to `importlib.metadata`. Every import of `scarf` triggers this logic, so avoid heavy work here.
- `examples/send_test_event.py` – runnable demo that exercises the logger against a test endpoint.
- `tests/test_event_logger.py` – comprehensive unit test suite; relies on `unittest` + `unittest.mock`
  (no third-party fixtures). Almost every behaviour in `ScarfEventLogger` has coverage here.
- `pyproject.toml` / `setup.py` – duplication is intentional. Both files must stay in sync for
  version bumps and dependency changes.

## ScarfEventLogger Behaviour

- Constructor enforces a non-empty `endpoint_url`, strips any trailing slash, accepts an optional
  default timeout, and reads `SCARF_VERBOSE` (unless an explicit `verbose` argument is supplied).
- Environment guards: analytics calls short-circuit when either `DO_NOT_TRACK` or
  `SCARF_NO_ANALYTICS` is set to a truthy string (`"1"` or `"true"` in any casing).
- Requests flow through a shared `requests.Session`, so headers/cookies persist between calls.
- User-Agent format: `scarf-py/<version> (platform=<os>; arch=<arch>, python=<major.minor.patch>)`.
  Any change to the header builder should keep tests in sync (`test_version_consistency`).
- Verbose mode prints configuration on init and detailed request/response data per `log_event` call.
  Tests assert on these strings; keep output wording stable or update assertions together.

## Testing & Tooling

- Core command: `pytest` (configured in `pyproject.toml` via `[tool.pytest.ini_options]`).
- Unit tests rely heavily on `unittest.mock.patch` for `requests.Session`, so remember to reset call
  history when extending scenarios.
- Ruff linting is optional but configured (`tool.ruff` + `tool.ruff.lint`). Run manually with
  `ruff check .` if you touch style-sensitive areas.
- For quick manual verification, use `python examples/send_test_event.py` (installs require `pip install -e .` first).

## Releasing & Versioning

- Bump versions in **both** `pyproject.toml` and `setup.py`; `scarf/version.py` will pick up the new
  value automatically.
- README already documents the tagging workflow (`git tag vX.Y.Z` → push tag triggers publish).
- `setup.py` still advertises `python_requires=">=3.7"` while the project metadata in
  `pyproject.toml` says `>=3.10`. Align these values if compatibility changes, and update tests if
  behaviour depends on specific Python features.

## Common Gotchas

- Forgetting to disable analytics in tests will hit the real network; always patch `requests.Session`.
- Since `log_event` re-raises request exceptions, callers outside tests should wrap calls in
  `try/except requests.exceptions.RequestException` (see the example script for the pattern).
- Any additional environment variable support should extend `_check_do_not_track()` first and then
  mirror coverage in `test_check_do_not_track`.

Armed with the above you should be able to triage most tasks without spelunking through the entire
codebase. Keep this file updated when you discover new quirks or architectural edges.
