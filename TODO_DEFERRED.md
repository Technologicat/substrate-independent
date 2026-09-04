# Deferred TODOs

## No CI for `scripts/`

*Cluster: ? · Cost: ? · Gate: a design call — see below · Filed: 2026-08-12*

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

## Coverage measures reach; what tests are for is grip

*Cluster: testing practice · Cost: S · Gate: none · Filed: 2026-09-04*

A Goodhart observation with a concrete case behind it, worth a section in
`field-observations.md`. Juha's framing, from measuring Raven's coverage on 2026-09-04; filed rather than
written up because a proper write-up wants bandwidth the day did not have.

**The claim.** Coverage measures whether a line *ran*. What anyone actually wants to know is whether a test
would *fail if the behaviour were wrong*. Those come apart in both directions, and only one of the two is
cheap to compute — which is the whole reason the proxy took hold.

**The mild half, which is a blind proxy rather than a gamed one.** Raven's `gui` test group adds fourteen
tests and *zero* measurable coverage: it asserts behaviour under a mapped window on code the headless tests
already execute. Nobody was optimising anything; the measure simply cannot see what those tests do. Anyone
steering by coverage would never write them, and would be worse off.

**The sharp half is the ordinary Goodhart.** Once the number is a target it is met by tests that execute
lines and assert nothing — getters, `__repr__`s, imports — and the measure rises while correctness does not.

**The direct measure exists and is already a fleet habit**: the negative control, patching the behaviour
back out to confirm the test rejects it. That asks exactly what coverage proxies for. On 2026-09-04 it
caught two Raven tests with full coverage and no power at all — one that called the method a button
*should* have been bound to, and so passed against a button bound to a no-op, and one that never exercised
the fix it was written for. Both executed every line; neither could fail. This is the argument for why that
habit is worth its cost, which the habit's own write-ups do not currently make.

**What keeps coverage worth measuring anyway**, and the part a write-up should not omit: it is strong
evidence of *absence* and weak evidence of *presence*. 0% means untested, full stop — which is how
`raven/papers/pdf2bib.py` was found. A high number means the lines ran and nothing more, and a *low* number
still needs a reason before it means anything: Raven's `chat_controller.py` at 12% is a real gap, while six
files at 0% are app entry points that cannot be imported under pytest at all.

Concrete Raven facts live in that repo — `CLAUDE.md` beside the test markers, and `TODO_DEFERRED.md` under
*"Modules worth testing that are not app entry points"*. What belongs here is the general shape.
