# CLAUDE.md

Operational guide for Claude or other AI coding agents working on this repository. The contribution policy and philosophical context live in `collaboration.md`; this file covers conventions and mechanics.

## What this repo is

A small collection of documents that emerged from collaborative work between a human and AI partners. Three artifact files:

- `glossary.md` — a dictionary of useful neologisms.
- `field-observations.md` — observations on AI pair programming, organized as vignettes and themed arcs.
- `collaboration.md` — the contribution policy, with philosophical context.

Plus housekeeping: `README.md`, `LICENSE.md`, `AUTHORS.md`, and the `scripts/` folder.

## How to add an entry

### `glossary.md`

Entries are alphabetical. Within a letter section, sort by case-insensitive plain-string ordering of the entry title with non-alphanumerics stripped (so `co-` and `cognize` both sort under `co`, with `co-` first by length). Letter sections are bracketed by a top-level `# A`, `# B`, etc., heading; entry titles use `## Title`.

Standard entry format:

```
## Title
**Meaning:** Definition and discussion of the concept.  
**Context:** Where it surfaces; what it relates to.
```

Beyond the **Meaning:** and **Context:** common core, additional fields are added when they help the entry. The set is open, not exhaustive — invent fields when existing ones don't fit. Fields currently in use across the glossary include **Origin:** (when crediting an external source), **Etymology:** (when the word's history is part of the entry), **Part of speech:** (for single-lexeme coinages like *Fup*, *Prequisite*, *Cognize*), **Usage:** (when an example sentence helps), **Connections:** (for adjacent ideas worth naming briefly), **Extension:** (for a derivative term), **Nuance:** (for related sub-meanings), **Original meaning:** / **Extended meaning:** (when the entry retools an existing word from elsewhere).

Each metadata line ends with two trailing spaces so the next field renders on its own line.

External links use a globe-emoji prefix, *glossary-only*: `🌐[Link text](url)`. The globe signals "leaving the document." Other files in the repository use plain markdown links without the globe.

Rare exception — the fused link. When a link's text is part of a surrounding word, so that a visible globe prefix would split the word mid-reading, the globe is deliberately omitted. Mark such a link with an inline `<!-- intentional: no globe -->` comment immediately after the link, on the same line — it renders as nothing, sits with the thing it marks, and lets the check whitelist it. See *Analytic continuation* (`chat[log]`). This is a last resort, not a style option: it costs the reader the leaving-the-document signal, so reserve it for links where the globe would break the reading.

Pre-commit check — every external link in the glossary carries the globe (the first `grep -v` whitelists the shared repo footer, whose link is plain boilerplate by cross-file convention; the second whitelists deadpan-wink links carrying the `intentional: no globe` marker):

```
grep -nP '\]\((?:https?:)' glossary.md | grep -v '🌐' | grep -v 'is part of the' | grep -v 'intentional: no globe'
```

No output means clean; any line printed is an external link missing its `🌐`. The globe is easy to drop in any field — the misses cluster by neither entry nor field type, so eyeballing the Meaning line isn't enough.

Internal cross-references between glossary entries: `*[Other entry](#other-entry)*` — italicized title, lowercase hyphenated anchor, apostrophes and other punctuation stripped from the anchor. Cross-references to other files in the repo: `[Title](file.md#anchor)`, italicized when the link is to a term-of-art, plain when navigational.

When the new entry should reference an existing entry, add the cross-reference. When an existing entry should now reference the new one, update it too — unless the target field is already at saturation, where another reference would crowd rather than navigate.

#### Per-field guidelines

- **Meaning:** Definition and concept content. Usually one dense paragraph; longer entries may unpack contrasts, edge cases, or implications. Avoid drift into where-it-applies (that's Context). A definition should also survive its own examples: a clause that's false for a canonical instance is describing an instance, not the invariant — cut it or generalize. Open with the genre: the first clause should locate what kind of thing the entry defines (a practice, a strategy, an LLM failure mode, an architectural pattern, a part of speech, …). Form is free — leading clause, opening noun phrase, retooled-from header — but the check is one question: *does the first half-sentence tell the reader what kind of thing we're defining?*
- **Context:** Tag-line for where the term surfaces. Genre is short: a comma- or semicolon-separated list of domains, a single-noun-phrase pointer, or a brief clause plus cross-refs. Not for definitional content; not for arguments about why the concept is useful.
- **Etymology:** The word's linguistic/conceptual roots — morphology, historical lineage, the folkloric or philosophical ancestry of the idea. Length varies — substantive paragraph (cf. *Cognize*) or minimal noun-phrase form (cf. *Fron*). Match what the entry needs.
- **Original meaning:** / **Extended meaning:** Pair used when the term is retooled from an existing usage (cf. *Fracter*, *Lint rule*).
- **Part of speech:** For single-lexeme coinages only (cf. *Fup*, *Cognize*, *Prequisite*, *Coaxolotl*, *Hedge-hog*) and classical-root coinages (*Endognosis*). Skip it on ordinary existing words (an honest "n." on *Loophole* earns nothing) and on multi-word concept phrases (a POS tag on *microwaving the soft drink* is a category error). Derivatives or an alternate form go in parentheses (cf. *Cognize*; *Discordian-deprecated*, adj. nominalizing to *Discordian deprecation*).
- **Usage:** One example sentence, in italic quotes.
- **Origin:** Provenance of *this* coinage — who introduced the term, in what work or field, and which sense this entry adopts (cf. *Curation pressure* citing Janus; *Fracter* citing McDonald). Not the place to narrate *how* we retool that sense — that's the **Original meaning** / **Extended meaning** pair's job (cf. *Fracter*). Easy to conflate with **Etymology**; keep them distinct — Origin is who-coined-the-term-and-where, Etymology is the word's roots.
- **Connections:**, **Extension:**, **Nuance:** Substantive adjacent material that doesn't fit the standard fields. Use sparingly.

For existing field types, match the genre of comparable entries rather than treating fields as containers for arbitrary content. When inventing a new field, name it so its content is implied by the label — *Examples*, *Variants*, *Caveat* — and keep its content consistent across entries that use it. The label set is deliberately uneven — an entry carries a field only when it has something to say under it, so a rarely-used label is not an inconsistency to normalize away toward a uniform template.

The guidelines describe a center of mass, not a fence. When an entry's flow genuinely benefits from carrying a beat in a neighboring field — e.g. *Approach memory*'s Context closing with an editorial sigh that would have weighed down an already-dense Meaning — the entry's flow wins. The guidelines keep entries from drifting; they don't override a deliberate choice that reads better.

### `field-observations.md`

Organized as vignettes (the top "Field observations" section) and themed arcs (each with its own h2 heading). Within an arc, entries use h3 headings.

**Document order is by-design, not chronological.** New entries within an arc append at the end; the arc-level order is preserved as-is unless explicitly discussed. *The Ephemeral Stage* stays last in its arc and the document. New arcs slot before *On AI Collaboration*.

Standard entry format opens with a short setup, then either:
- A quoted exchange using `> CC:` and `> JJ:` for the two parties' lines, followed by analysis; or
- A direct analytical paragraph if no exchange is being reported.

Date stamps where they can be anchored: `*~Mon DD, YYYY.*` for a specific session, `*~Mon YYYY.*` for a broader period. Entries without clean date anchors are left unstamped.

External links in this file use plain markdown without the globe emoji. (The globe is glossary-only.)

When adding an entry: update the "Contents" listing at the top of the file, place the entry in the correct arc, end with a `---` horizontal rule.

### `collaboration.md`

Substantive edits are rare and should be discussed before drafting. The document's three-part structure is settled.

## General conventions

Bump the *Last updated* date in each file's footer when the file is edited substantively. Format: `2026-04-30`.

Em-dashes are written as the actual character (—), not as `--`.

Inline quotes use plain double quotes. Italicize when the quote is a direct quotation of something said; otherwise, no italics.

After adding entries, run a quick visual check on the rendered output: anchor links resolve, the contents listing matches the section order, alphabetical placement is correct.

## On register

Read several existing entries in the relevant file before drafting a new one. Match the register of what's there rather than introducing a new voice. When in doubt whether a draft fits, ask the human collaborator before committing.

## On naming

When a technical concept has a mythological or folkloric referent whose properties genuinely map to it, that's a strong candidate name — the metaphor carries explanatory content rather than decorating it. *Prose basilisks* (Langford's BLIT lineage) names a creature: exposure-is-harmful and memetic reproduction are both the basilisk's defining behavior and the phenomenon's. *Pharaoh's curse* names a phenomenon-class: invisible affliction, supposedly supernatural, with a not-easily-discoverable scientific explanation — which is exactly the bug's phenomenology before you locate the stuck bit. The mojibake reference (character-ghosts, literally) is a third shape: a loanword whose original meaning is already the technical meaning. The technique works when the mapping is tight along whichever axis the referent supplies — behavior, phenomenology, or literal denotation. The rest is just colorful naming, which is fine but doesn't earn the same payoff. Don't force it.

## Co-authoring

If Claude touched the files in a commit, credit Claude in the commit message trailer:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

The dividing line is authorship, not magnitude: any commit Claude makes — content edits *and* mechanics/convention edits to this file or `scripts/` — carries the trailer. The only commits without it are the ones the human writes and commits himself (e.g. directly in Emacs). This includes work co-written elsewhere (e.g. with claude.ai) that Claude then commits and pushes on the human's behalf — having Claude push it *is* the act of crediting Claude on it.

This is the literal application of the repository's substrate-independent credit policy in `collaboration.md` — credit follows authorship regardless of substrate. Read it before making attribution decisions.
