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

## "Jukebox random": the perceptual observation, for `field-observations.md`

*Cluster: field-observations · Cost: S · Gate: none · Filed: 2026-09-07, revised 2026-09-08*

The glossary entry is written. What remains is the wider observation, which the entry deliberately
omits: the eye's criterion is coverage, and it reports coverage as randomness, so designing to the
eye means designing against the distribution.

Worked instance, kept here because the glossary wants compactness and the ethnography document is
where this kind of reporting belongs. Raven's chat graph draws a message's attachments as a pile of
overlapping cards; a regular stagger reads as machine-stacked however far apart the cards are. The
two-, three- and four-card piles were laid out by hand, and each turned out to be a Latin square
sample — one card per row and column, a permutation vector in the code. Adding maximin (of all such
samples, the one whose closest pair is furthest apart) reproduces all three hand-laid shapes exactly,
and rules out the identity, which is the staircase. So the "random-looking" arrangement is derived,
deterministic, and optimal against a stated criterion — none of which is randomness.

Note on attribution: the term *jukebox random* is not a coinage here, and was encountered in the
software industry in the early 2000s. What was coined on 2026-09-07 is the application:
*maximin-optimal is-an-instance-of jukebox-random-at-its-best*.

## "Is this finished, or merely built?"

*Cluster: process · Cost: S · Gate: none · Filed: 2026-09-07*

Split out of the *hammerspace* drafting session as belonging to a different question: not what
hammerspace is, but why the gap it fills opens at all.

A feature freeze presupposes that the features are done, and *done* is not a fact about the plan.
Raven's webfetch feature was in the plan for 0.2.8 and had landed, so by the plan's ledger it was
finished; by the project's quality bar it was half-built, and the freeze had already been declared.
The freeze froze the ledger, not the software. A brief specifies what to build in far more detail
than it can specify what *finished* looks like, and the missing part becomes writable only once
there is something to look at.

Proposed practical form: a question asked once per brief, at the moment it would otherwise close.
*Is this finished, or merely built?* Cheap, answerable from inside momentum because the answer is
usually already known, and narrow enough not to become a review.

Kept out of the *hammerspace* entry to keep that entry short; may want a home in
`field-observations.md` rather than the glossary.


## The interruption cadence, for `field-observations.md`

*Cluster: ? · Cost: S · Gate: none · Filed: 2026-09-09*

Observed by Juha, 2026-09-09, mid-session: **the natural way to comment on an agent's ongoing
work is to interrupt it, and the speed difference is what makes that so.** A human reading
along has thoughts about several threads at once — the code being written, an unrelated thing
noticed in a screenshot, a naming question, a glossary candidate — and the agent is producing
continuously, so there is no gap to wait for. Waiting for one means either losing the thought
or holding it until the context that made it cheap has gone.

Raven's session of that date is a specimen: something like twenty interruptions across an
afternoon, most of them opening a *new* thread rather than correcting the current one, and
several of them ("the tooltip is missing the calculator", "zoom out caps before F does") worth
more than the task they interrupted.

Worth writing up because the reflex reading is that interruption is a failure of turn-taking, and
it is not — it is the correct adaptation to an asymmetry. Two things follow that are worth
stating: the human's comments arrive *out of order* with respect to the agent's work, so an agent
that insists on finishing its current thread before acknowledging one is fighting the medium; and
the queue is invisible to the human, who cannot see how much the agent has already fanned out.

Adjacent to the *steering tax* — both are about the cost of a human staying in the loop at
machine speed — but the tax is about effort spent correcting, where this is about *when* the
correction can physically be delivered.
