# Deferred TODOs

## No CI for `scripts/`

This repo is mostly prose, but `scripts/cc-log-extract.py` is real software with a
real test suite (`scripts/tests/test_cc_log_extract.py`, 14 tests, runnable either
standalone or under pytest). Nothing runs it automatically: there is no
`.github/workflows/` at all, so a change to the extractor is only as tested as
whoever pushed it remembered to be.

What it needs is the fleet baseline — pytest and `ruff check` on push and PR, actions
SHA-pinned, top-level `permissions: contents: read`. See the `ci-setup` skill.

The reason it isn't a five-minute job: the repo has no `pyproject.toml`, no lockfile
and no declared dependencies, and the script is deliberately dependency-free and run
by path rather than installed. So the fleet's `pdm install` CI shape doesn't fit as-is,
and the choice is either to scaffold packaging for a docs repo that otherwise doesn't
want it, or to write a smaller workflow that runs `python3` against the test file
directly. That's a design call, not a chore.

Noticed while fixing the `cc-log-extract` timestamp rendering (2026-08-12).
