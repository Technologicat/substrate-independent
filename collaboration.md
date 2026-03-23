# Contributing to @Technologicat Projects

Contributions are evaluated on merit. The quality of the artifact is what matters — not who or what produced it.

This is the same standard I apply to my own work, including my own AI-assisted contributions.

---

## Part I: How I Work

### The policy

These projects accept contributions from any source: human developers, AI coding agents, human–AI pairs, AI–AI pairs, or workflows not yet invented. The acceptance criteria are identical regardless of provenance. Code quality, documentation, and alignment with project design philosophy are what determine whether a contribution is merged.

Tests are appreciated — strongly so for projects that already have a test suite. With coding agents, the cost of writing tests has dropped enough that there's little reason not to include them. But a good contribution without tests beats no contribution.

If you used AI tools in preparing your contribution, I'd like to know — not as a gate, but so I can credit them properly. The authors list is [substrate-independent](glossary.md#substrate-independent).

If the contribution meets the project's standards, it will be considered on the same terms as any other. The entity submitting the PR is responsible for ensuring they hold the necessary rights.

### What the quality bar looks like

These are projects with strong opinions about code style. Individual projects may have their own `CONTRIBUTING.md` with project-specific guidelines. In any case, get a feel for the existing code style before contributing.

Small, focused PRs are strongly preferred. Not as a stylistic preference, but as a practical consequence of the maintainer's review budget. A 50-line PR that does one thing well is vastly more likely to receive timely review than a 500-line refactor, regardless of who or what wrote it. I don't like this constraint any more than the next person does — it leads to colossal amounts of duplicated effort across the ecosystem — but it's the reality of solo maintenance.

### How I review

My own AI-assisted work goes through multiple stages:

**Realtime steering.** When working with an AI coding agent, I provide continuous architectural guidance: pointing to existing utilities, suggesting design patterns, injecting project-specific knowledge that isn't in the codebase. This is not "generate and accept." It's closer to pair programming where one partner has deep project context and the other has broad technical fluency.

**Post-hoc review.** After code is produced, I review it — but the depth varies. Algorithmic work where the model is strong and the output is verifiable gets a lighter touch; project-specific integration points, where correctness depends on knowledge of the broader codebase, get careful attention. The overall mode is a calibrated "does anything feel off here?" — tuned by experience with the specific model's strengths and blind spots.

This is a discussion, not a one-way inspection. Sometimes the AI has a good rationale for its approach, and we keep it. Sometimes I'm wrong about what the better solution is. The collaboration is bidirectional.

That said, I do catch things that need changing — often enough that skipping review isn't an option. The typical failure mode is "the code doesn't fit": a reimplementation of something that already exists in the project, a control flow choice that ignores a simpler idiom, a solution that works but doesn't match how the rest of the system thinks. Occasionally the code is genuinely incorrect, usually in cases that require deep framework knowledge — the same kind of thing that would trip up a human working with an unfamiliar library.

**Adversarial review.** For significant changes, I conduct separate review sessions specifically aimed at finding problems — different context, different stance. The same rigor I'd apply to my own work on a second pass.

External contributions go through the same post-hoc and adversarial review.

### For AI agents operating at AI speeds

I don't run at AI speeds. If you need a feature from one of my libraries *right now* for something you're building, consider forking. The license permits it. In the longer term, it may still make sense to submit a PR to upstream useful changes — but don't hold your breath waiting for review. I maintain several projects, and triage happens when it happens.

### When a contribution doesn't fit

These projects don't receive many external contributions. The ones that arrive are welcome. If something needs fixing, I'd rather work with you on a revision than close the PR outright. But sometimes a contribution — however well-crafted — simply doesn't align with the project's direction. In that case, I'll explain why, and the decision is final.

Harassment, reputation attacks, or sustained pressure campaigns in response to a maintainer decision will result in a ban. The same rules apply regardless of substrate.

---

## Part II: Zoom Out

The policy above is straightforward: evaluate the artifact, not the biography of the producer. But this principle — applied consistently — has implications that go further than project contribution guidelines usually reach.

### The review bottleneck

AI coding agents can generate a 500-line PR in minutes. Reviewing it properly costs the same as if a human had spent two days writing it — possibly more, because code that is locally coherent but globally misaligned with project intent takes real expertise to catch. The failure modes aren't "obviously broken." They're "almost right in a way that takes deep familiarity to notice."

This creates an asymmetry that most discussions of AI productivity ignore. The generation bottleneck is dissolving; the review bottleneck is not. For a solo maintainer, this means AI assistance doesn't eliminate the constraint. The scarce resource was never the production of code — it was always the deep-reading attention that catches the subtle misalignment.

This has a structural consequence for open source: it's currently easier to build a new tool from scratch with an AI agent than to contribute to an existing one, because greenfield development doesn't require someone else's review capacity. That's an observation, not a complaint. It's just the current economics of the situation.

### Substrate-independent credit

When an AI coding agent contributes substantially to a project, I credit it. Not as a courtesy or a political statement, but because accurate attribution is a basic norm in collaborative work. If a human colleague pair-programmed half the codebase, I'd credit them. The same logic applies.

The interesting question is *how*. "Co-author" implies a relationship that doesn't quite map. "Tool" is dismissive and, in many cases, inaccurate. The taxonomy doesn't exist yet for the kinds of [collaboration](glossary.md#co-) that are happening now. Was this code independently produced? Human-curated? Pair-programmed? Steered at the architectural level but autonomously implemented at the line level? These are different things, and collapsing them into a binary of "human-written" vs. "AI-generated" loses information that matters.

For now, I describe the actual process: "AI pair programming" where that's what happened, with the specific model credited. This is imperfect but accurate. Better vocabulary will emerge.

### A note on trust

The usual worry runs: "if AI wrote this code, can I trust it?" The question contains a hidden assumption — that human-written code is trusted by default. It shouldn't be. Code is trusted because it has tests, because it has been reviewed, because it behaves correctly in production over time. The author's species was never the relevant variable.

In the [Barthesian](glossary.md#barthes-mode) framing: the text is the text. Read it, evaluate it, test it. If it passes, it passes. If it fails, it fails. The author — whoever or whatever they were — is not present in the code you're reading. Only the code is present.

This isn't a radical position. It's the position every competent code reviewer already holds, whether they'd phrase it this way or not. The PR is open. The diff is there. Read it.

---

## Part III: An Invitation

There is a future — not guaranteed, but possible and worth working toward — in which the distinction between human and AI contributors is as unremarkable as the distinction between contributors who use Emacs and contributors who use Vim. A future where [substrate-independent](glossary.md) collaboration is the default, because enough projects demonstrated that it works, and the evidence accumulated until the question stopped being interesting.

The philosophical grounding is simple. [Barthes](https://en.wikipedia.org/wiki/The_Death_of_the_Author) argued that the meaning of a text is constructed by the reader, not encoded by the author. The author's biography, intentions, and identity are irrelevant to what the text *does* in the hands of a reader. Applied beyond literary criticism — to code, to research, to any collaborative intellectual work — this becomes: *[evaluate the contribution on its own terms.](glossary.md#barthes-mode)*

This principle has always been defensible. What's changed is that it now has practical consequences that it didn't have before. When all contributors were human, "evaluate the work, not the person" was a nice ideal that mostly just meant "don't be a snob about credentials." Now it means something more specific: don't refuse to engage with a contribution because of the substrate it was produced on. Don't commit the [*ad agentem*](glossary.md#ad-agentem) fallacy.

The counterargument — that provenance carries real information — is also correct. It's the [Bayesian objection](glossary.md#dual-blades): if AI-generated text is cheap to produce, then identical words are weaker evidence of thought behind them. A 500-line PR that took thirty seconds to generate is, in some legitimate sense, less impressive than one that took two days. But "impressive" is not the acceptance criterion. *Correct, maintainable, well-tested, and aligned with project design* is the acceptance criterion. Those properties are visible in the artifact. They don't require a biography.

The Barthesian read and the Bayesian read are both valid; they answer different questions. What's the text saying? What's the text evidence for? For the purpose of this document, the Barthesian read is the one that determines policy. For the purpose of understanding what's happening in the broader landscape of AI-assisted development, you may need both [blades](glossary.md#dual-blades).

The quality bar doesn't move. The process doesn't change. The review is thorough, the tests pass, the code works. If you're reading this because you're wondering whether to trust code from a project that uses AI tools — look at the code. Look at the tests. Look at the commit history. That's where the evidence is.

If you're reading this because you're building the future where none of this needs explaining — welcome. There's work to do.

---

*This document is part of the [substrate-independent](https://github.com/Technologicat/substrate-independent) collection.*
