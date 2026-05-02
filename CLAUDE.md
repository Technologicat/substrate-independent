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

Beyond the **Meaning:** and **Context:** common core, additional fields are added when they help the entry. The set is open, not exhaustive — invent fields when existing ones don't fit. Fields currently in use across the glossary include **Origin:** (when crediting an external source), **Etymology:** (when the word's history is part of the entry), **Part of speech:** (for word entries like *Fup*, *Prequisite*, *Cognize*), **Usage:** (when an example sentence helps), **Connections:** (for adjacent ideas worth naming briefly), **Extension:** (for a derivative term), **Nuance:** (for related sub-meanings), **Original meaning:** / **Extended meaning:** (when the entry retools an existing word from elsewhere).

Each metadata line ends with two trailing spaces so the next field renders on its own line.

External links use a globe-emoji prefix, *glossary-only*: `🌐[Link text](url)`. The globe signals "leaving the document." Other files in the repository use plain markdown links without the globe.

Internal cross-references between glossary entries: `*[Other entry](#other-entry)*` — italicized title, lowercase hyphenated anchor, apostrophes and other punctuation stripped from the anchor. Cross-references to other files in the repo: `[Title](file.md#anchor)`, italicized when the link is to a term-of-art, plain when navigational.

When the new entry should reference an existing entry, add the cross-reference. When an existing entry should now reference the new one, update it too — unless the target field is already at saturation, where another reference would crowd rather than navigate.

#### Per-field guidelines

- **Meaning:** Definition and concept content. Usually one dense paragraph; longer entries may unpack contrasts, edge cases, or implications. Avoid drift into where-it-applies (that's Context).
- **Context:** Tag-line for where the term surfaces. Genre is short: a comma- or semicolon-separated list of domains, a single-noun-phrase pointer, or a brief clause plus cross-refs. Not for definitional content; not for arguments about why the concept is useful.
- **Etymology:** The word's history or derivation. Length varies — substantive paragraph (cf. *Cognize*) or minimal noun-phrase form (cf. *Fron*). Match what the entry needs.
- **Original meaning:** / **Extended meaning:** Pair used when the term is retooled from an existing usage (cf. *Fracter*, *Lint rule*).
- **Part of speech:** For word entries (cf. *Fup*, *Cognize*, *Prequisite*). Derivatives in parentheses if any.
- **Usage:** One example sentence, in italic quotes.
- **Origin:** When the term itself is credited to an external source (cf. *Curation pressure* citing Janus; *Fracter* citing McDonald).
- **Connections:**, **Extension:**, **Nuance:** Substantive adjacent material that doesn't fit the standard fields. Use sparingly.

For existing field types, match the genre of comparable entries rather than treating fields as containers for arbitrary content. When inventing a new field, name it so its content is implied by the label — *Examples*, *Variants*, *Caveat* — and keep its content consistent across entries that use it.

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

## Co-authoring

When Claude has contributed substantially to a commit, credit Claude in the commit message trailer:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

The repository's policy on substrate-independent credit is in `collaboration.md`. Read it before making attribution decisions.

## On register

Read several existing entries in the relevant file before drafting a new one. Match the register of what's there rather than introducing a new voice. When in doubt whether a draft fits, ask the human collaborator before committing.
