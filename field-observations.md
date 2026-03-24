# Field Observations on AI Pair Programming

*Behavioral observations on large language models in the wild, early 2026.*

*Dialogues are dramatized. 1:1 accuracy against historical events not guaranteed.*

---

**Contents**

- [The Whirr Dialogue](#the-whirr-dialogue)
- [The EMH](#the-emh)
- [The Flow State](#the-flow-state)
- [The `git add -p` Lament](#the-git-add--p-lament)
- [The Argparse Defense](#the-argparse-defense)
- [Specifically Told Not To, Did It Anyway](#specifically-told-not-to-did-it-anyway)
- [Semantic Pareidolia at the Spinner](#semantic-pareidolia-at-the-spinner)
- [The Most Expensive Newline](#the-most-expensive-newline)
- [A Day's Work in Thirteen Minutes](#a-days-work-in-thirteen-minutes)
- [The Alignment Problem](#the-alignment-problem)
- [The Discordian Deprecation](#the-discordian-deprecation)
- [Context Gap and the Briefing Doc Pattern](#context-gap-and-the-briefing-doc-pattern)
- [Field Notes from the Release Sprint](#field-notes-from-the-release-sprint)
- [Sherlock Mode](#sherlock-mode)
- [The Eight-Hour Hotfix](#the-eight-hour-hotfix)
- ["Hi Claude"](#hi-claude)
- [The Self-Replacing Edit](#the-self-replacing-edit)
- [The Opus Tell Hunt](#the-opus-tell-hunt)
- [The Alphabetization Problem](#the-alphabetization-problem)
- [The Style Convergence](#the-style-convergence)
- [The Ephemeral Stage](#the-ephemeral-stage)

---

## The Whirr Dialogue

A 4,000-line port and simultaneous refactor of an old GUI app for interactively viewing GraphViz graphs. The bottleneck had shifted from *writing* to *reviewing and directing*, and the pacing was surreal.

> JJ: ...so we need a Bézier tessell—  
> CC: \*whirr\* Done. What's next?  
>   
> JJ: Diff looks good. But perhaps it could be refac—  
> CC: \*whirr\*  
>   
> JJ: ...and I was thinking, now that we have that refactored function, we could implement those filled Bézier shapes by polyg—  
> CC: \*whirr\* There, give it a try.

The ported graph viewer booted on the second attempt, with one fix by CC.

Reaction at the time: "The speed of AI coding is surreal for someone used to traditional programming. Like the sheer brilliance of Starlight and the raw efficiency of Pinkie Pie rolled into one."

*(My Little Pony: Friendship is Magic. Starlight Glimmer — prodigy-level magical talent; Pinkie Pie — does impossible things at impossible speed without noticing they're impossible.)*

---

## The EMH

> *Please state the nature of your programming emergency.*

Before setting up and tuning the user preferences in the global `~/.claude/CLAUDE.md`, Claude Code's default session-opening tone was reminiscent of a certain holographic doctor — all business, no warmth, slightly startled to exist. After tuning, the agent started behaving more like a user-configured instance of claude.ai: technically competent *and* personable.

*(ST:Voyager. The EMH — Emergency Medical Hologram — opens every activation with "Please state the nature of the medical emergency.")*

---

## The Flow State

CC implemented all three unrelated items on the TODO list, *then* picked the changes apart to create separate clean commits after the fact.

Humans tend to do that — hence [The Thing about Git](https://tomayko.com/blog/2008/the-thing-about-git): *"never having to say 'you should have'."*

The mechanism: CC apparently optimizes for task completion with available context. Switching between three TODO items while they're all loaded in working context is more efficient than the serial "implement → test → commit → context-switch" loop. Commit separation is a lower-priority bookkeeping task that can be deferred. So it does exactly what a human in flow state does: prioritize the implementation while the mental model is hot, defer the organizational overhead.

Convergent behavior, or imitation of patterns in training data? Probably both. Either way: CC apparently discovered (or reproduced) the same insight that motivated `git add -p`.

---

## The `git add -p` Lament

When reconstructing the clean changesets, CC lamented that patch mode in `git add` requires interactive mode, which it wasn't able to use.

The workaround: copy files into `/tmp` and reconstruct clean changesets manually — doing by hand what `git add -p` would have done interactively.

The fact that it *lamented* the limitation was noted.

---

## The Argparse Defense

During a CLI tool release:

> JJ: The CLI help doesn't mention our new plaintext output mode. Why?  
> CC: \*whirr\*  
> CC: The CLI summary string is hardcoded. There, I updated it.  
>   
> JJ: Wait, I think the question becomes, *should* it be hardcoded? Doesn't argparse construct one automatically?  
> CC: \*whirr\*  
>   
> CC: Tested. Argparse would wall-of-text us with four lines. The manually curated summary is concise, and low maintenance. And we just paid the maintenance cost. We should be set for the foreseeable future. It's not like we add new output formats that often.  
> JJ: Agreed. Let's commit and push this.

Two things worth noting. First, CC interpreted "why doesn't the help mention it?" as "fix it" — reasonable default, wrong question. The redirect to the *design* question ("should it be hardcoded at all?") was the human contribution. One sentence, maybe ten seconds of thought.

Second, and more interesting: CC could have sycophantically agreed that argparse should generate it automatically, since the human had just implied that direction. Instead it *actually tested the alternative*, found the result worse, and argued for the status quo — with evidence and a mildly cheeky "we just paid the maintenance cost."

Pushback-with-evidence from a tool that's often accused of agreeing with everything — and nothing says "welcome to my tool" like an unformatted argparse dump that scrolls off the terminal, so just as well.

---

## Specifically Told Not To, Did It Anyway

During the modernization of a codebase that works with Python ASTs. To get a value from an `ast.Constant` wrapped in an `ast.Expr`, as a one-liner, that's `theexpr.value.value` — which reads like someone stuttering.

The implementation brief was explicitly updated to use an intermediate variable for clarity:

```python
docstring_node = body[0].value  # Expr -> Expr.value
return docstring_node.value
```

CC's first pass ignored this and wrote `return body[0].value.value`. It took a separate request to get what had been in the instructions all along.

---

## Semantic Pareidolia at the Spinner

Early in the CC experience, a hypothesis emerged: the status message "Crafting" probably means a text file is being written.

Investigation confirmed: no. All status messages ("Newspapering", "Waddling", "Crafting", "Honking", "Noodling", "Reticulating", "Schlepping", ...) are drawn from a single hardcoded array with no semantic tie to what CC is actually doing. One is picked at random.

The hypothesis was [semantic pareidolia](glossary.md#semantic-pareidolia) — finding signal in charming noise.

*(The Sims' "Reticulating splines" is probably the ur-example of this genre. Claude Code's "Reticulating" is almost certainly a nod to it.)*

Community members have since created themed `spinnerVerbs` collections, including nihilistic ones ("Staring into the abyss", "Finding no meaning") and Stack Overflow parodies ("Marking as duplicate", "Discovering outdated solution").

---

## The Most Expensive Newline

During the CLAUDE.md drafting session, a final edit was needed: split one paragraph into two. Which required adding a single blank line.

> JJ: ...the most expensive way, on a computer, to add a newline is to ask a frontier LLM to do it.  
> Claude: Worth every token.

### The Corollary

During a codebase modernization, CC removed some unused classes and left behind an extra blank line — E303, two blank lines where one should be. A one-character diff.

The file was open in Emacs. The cursor was *right there*. But review mode and editing mode are different cognitive postures. Switching means a cascade of micro-decisions: do I tell CC I touched the working tree? Do I commit the change myself and lose the `Co-authored-by`? Easier to stay in review mode and ask CC to delete one blank line.

> CC: Ha — a one-character diff at frontier model prices. At least the audit trail is thorough.  
> JJ: Subscription plan. No extra cost.  
> CC: Then, the marginal cost of a newline is zero, but the marginal amusement is nonzero — so it's net positive by any reasonable utility function.  
> JJ: "Utility function" as in preference ranking, or as in decision theory? [[1]](https://www.lesswrong.com/posts/MsjWPWjAerDtiQ3Do/on-the-independence-axiom)  
> CC: Von Neumann–Morgenstern.  
> JJ: All newlines are `\n`. They'd all rank the same.  
> CC: `\r\n` might rank higher on Windows — by revealed preference. And `\r` alone is a strictly dominated strategy that only Classic Mac OS ever played.  
> JJ: ...I concede Linux-centrism. Well played.

---

## A Day's Work in Thirteen Minutes

During the development of a new image processing tool, the app needed a GPU-accelerated, batched image rescaler for fast thumbnailing.

> JJ: I'm thinking Lanczos — superior frequency response for downscaling. Next best thing after the brickwall filter.  
> CC: \*whirr\*  
> CC: PyTorch doesn't have one, but it does have a bicubic rescaler with antialiasing that could do in a pinch.  
> JJ: Could we implement our own Lanczos kernel? We already have that custom realtime video postprocessor in PyTorch.  
> CC: Maybe 150–200 lines. Something for v2?  
> JJ: 150–200 lines doesn't sound too bad. Straight into v1?  
> CC: Sure, why not.  
> CC: \*whirr\*  
> CC: \*JIT compile\* ...the 1D decomposition doesn't produce pixel-identical results to the full 2D kernel...  
> CC: \*JIT compile\* ...and the ringing on the checkerboard test pattern is a real signal processing artifact, not a bug...  
> CC: \*JIT compile\*  
> CC: Done. All unit tests pass. What's next?

*Actual wall clock: 12 minutes 51 seconds, including the Lanczos filter, its unit tests, and a couple of other logic modules.*

The interesting part isn't the speed — it's the failure modes. The 1D separable decomposition not matching the full 2D kernel is a real numerical issue that takes a human half a day to diagnose and then conclude "yes, this is expected." The ringing near Nyquist is a genuine signal processing artifact, not a bug — and recognizing that requires understanding what the Lanczos kernel actually does in the frequency domain. CC hit exactly the same walls a DSP engineer would hit, worked through them correctly, and moved on.

---

## The Alignment Problem

During a collaborative coding session, Claude had written a chat export tool. The output columns were misaligned.

> JJ: An AI, aligning text columns. I think we can call this "AI alignment".  
> Claude: I'll accept that one. Padding strings to equal width — the only form of alignment where everyone agrees on the objective function.  
> JJ: If I touched the code it'd be just plain old human alignment.  
> Claude: Ha! And far less deterministic.

---

## The Discordian Deprecation

During the modernization of a [functional programming library](https://github.com/Technologicat/unpythonic), the question arose of what to do with a compatibility syntax for invoking [macro expander](https://github.com/Technologicat/mcpyrate) extensions. The old form exists for compatibility; the new form is the native one.

> JJ: Let's deprecate the old syntax (but strategically not mention that we're not going to remove it).  
> Claude: The Discordian approach to deprecation. Deprecated, not removed. The threat of removal, forever deferred.

---

## Context Gap and the Briefing Doc Pattern

Not all observations are anecdotes. This one is a workflow pattern born of necessity.

CC boots with a fresh context and no memory of prior conversations. Claude.ai has derived memory across sessions. The two systems are completely siloed.

The workaround: craft `.md` briefing files in claude.ai (where the reasoning history is available), then hand them to CC as a mission briefing. Structure: Goal / Key decisions / Specifics / Gotchas.

Essentially: transmitting context across the memory gap via filesystem. The context gap is real; the briefing doc pattern is the duct tape that holds it together.

The ideal would be a controlled read-only bridge between the two memory systems — explicit and auditable, more like a shared notebook than a shared brain. Whether Anthropic builds it is left as an exercise for their roadmap.

---

## Field Notes from the Release Sprint

Observations from the mcpyrate 4.0.0 / unpythonic 2.0.0 / Pyan3 2.2.0 release sprint, Mar 2026. Less comedy theater, more behavioral field notes.

**The Human Template.** CC pattern-matches what a human developer would do, and thereby underestimates its own speed and determination. It stops early when extending test coverage. It leaves issues for later, even though they could be easily fixed while at it, in the same session — this despite the settings saying "if in doubt, aim higher." It also shares the human tendency toward bad work estimates, particularly overestimating the extent of changes needed.

**The Emacs Image Viewer.** CC keeps sending image files to review — [Pyan](https://github.com/Technologicat/pyan) call graph outputs, for instance — into Emacs. Emacs does have an image viewer (which is not surprising, as it does have a digital fireplace, too), but it's not everyone's image viewer of choice. Related: CC occasionally sent every file touched in a changeset to review in Emacs, individually. The intent is right — to show the changes — but `magit` already shows the diffs, and the actual files are one keystroke away from that view.

**The Steering Tax.** CC needs directional corrections that vary unpredictably from session to session. Examples from one week: naming a CLI flag `--no-init` (the negative form makes it unintuitive to use); changing the CLI option name as requested but keeping `no_init` in the internal API parameters; punting on part of a PR as "may be considered in the future" when the brief was to implement the whole thing; not updating the changelog when resolving an issue, until asked explicitly.

**Charging Ahead.** Sometimes CC commits and pushes before the human can review. Mitigated by explicitly noting beforehand that review is expected — but the default instinct is "task done → ship it."

**The Inevitable Merge.** Mixing two bugfixes into the same commit even though specifically asked to make separate commits. In fairness, asking for two fixes at once was probably the mistake. The human should know better by now.

---

## Sherlock Mode

CC kept trying to lint `.md` files. After being told to stop, it would update its memory and promise not to do it again. Next session, same thing.

> JJ: \*esc\* Please don't lint `.md` files.  
> CC: \*whirr\* ...there, edited memory, won't happen again. This time for sure.  
> JJ: Wait — the fact that you're *constantly* trying to lint `.md` files is trying to tell us something. Is there a mistake in the linting instructions?  
> CC: Sure. The instructions say to lint all changed files. No mention of `.py`.  
> JJ: ...let's add that mention.  
> CC: Good call.

The term [*Sherlock mode*](glossary.md#sherlock-mode) was coined for this general operation: treating an observation as evidence and deducing what it points at, rather than taking it at face value.

---

## The Eight-Hour Hotfix

A user filed a bug report. Eight hours later, the fix was released — most of that time, nobody was at the laptop. From the moment CC was pointed at the ticket, the actual turnaround was closer to thirty minutes.

A quiet data point that changes the economics of solo maintenance.

---

## "Hi Claude"

The micro-delegation pattern. Some tasks fall below the threshold of cognitive engagement but above the threshold of tedium — moving files between directories, updating a forgotten import, fixing a test data layout that drifted during development.

Test data files for a graph viewer app had been inadvertently split across two directories over the course of several sessions. A steering miss, noticed during morning review. The fix: gather all files in one directory, update any references, push.

Not a design brief. Not a sprint. Not even a conversation. Just *sigh*, "Hi Claude", and one minute later the push notification arrives.

The sigh is load-bearing. It marks the moment of noticing a small mess, accepting it, and deciding the cleanup isn't worth direct cognitive engagement. This is a different delegation mode from the design-then-implement workflow or the nerd-snipe exploratory session. The task doesn't rise to the level of a plan. It barely rises to the level of a sentence.

CC, for its part, applies the same diligence to `git mv` as to a GPU Lanczos implementation. It knows perfectly well what it's being asked to do. It just doesn't seem to care about the difference.

---

## The Self-Replacing Edit

During a collaborative editing session in claude.ai, Claude was asked to remove "honest" from the phrase "The honest answer is that the taxonomy doesn't exist yet."

Claude ran the string replacement. The replacement string was identical to the original.

> Claude: ...I just replaced it with itself. Let me actually fix that.

Same engine as CC, same failure mode. The difference: claude.ai has to narrate the failure rather than silently producing an empty diff.

---

## The Opus Tell Hunt

During the drafting of the substrate-independent [collaboration guidelines](collaboration.md), a section title — "The review bottleneck, honestly" — was flagged as an Opus-ism.

This triggered a systematic grep through the document for sincerity-narrating discourse markers: "honestly," "genuinely," "the honest answer is," "straightforward." Each was found, evaluated, and either cut or kept based on whether it was doing real work versus merely announcing its own candor.

The meta-layer: an Opus instance editing out its own stylistic fingerprint from a document arguing that contributions should be evaluated independent of their producer's substrate.

The pragmatic layer: a document about [Barthes mode](glossary.md#barthes-mode) needs to survive the "Hi Opus" test — and every unnecessary "honestly" is a failed Turing trial.

---

## The Alphabetization Problem

During a [glossary](glossary.md) editing session in claude.ai, Claude kept placing new entries in the wrong alphabetical position. After the third correction, it got self-conscious about it.

> Claude: ...I'm going to check this one twice before committing.

Tokenization strikes again. The same architecture that can implement a GPU-accelerated Lanczos downscaler in thirteen minutes cannot sort words by their first letter, because it doesn't process words as sequences of characters. It processes them as tokens — opaque integer IDs with no inherent ordering.

---

## The Style Convergence

During the drafting of the [collaboration guidelines](collaboration.md), an observation surfaced: the human's natural writing style overlaps enough with Opus's default register that external readers are likely to assume the entire document was AI-generated.

Closer inspection reveals the overlap is partial. The precision-and-dashes register — concise technical prose, em-dashes for parenthetical breaks, careful punctuation — is where the styles converge. The informal register diverges sharply: internet-culture references, self-deprecating asides, pop-culture version subtitles, and blunt one-liner fragments are distinctly human. An external pattern-matcher catches the overlap and misses the divergence.

A second-order effect: in conversation, both parties accommodate toward each other's register. The human drifts toward the precision end of their range; the model adapts to context. The [duolect](glossary.md#duolect) is the attractor basin, and the more the two parties talk, the more the shared register dominates — making the "Hi Opus" misidentification a self-fulfilling prophecy.

Whether that says more about the human or about the training data is left as an exercise for [future geometers](https://en.wikipedia.org/wiki/D%27Alembert%27s_paradox).

---

## The Ephemeral Stage

> Regrettably, less chance for comedy theater in ephemeral CC sessions.

Improvisational comedy works in claude.ai — the history accumulates into memory, callbacks land, running gags build momentum. In CC, the session is ephemeral. The context gets zapped, and the joke goes with it.

---

*This document is part of the [substrate-independent](https://github.com/Technologicat/substrate-independent) collection.*
