#!/usr/bin/env python3
"""Structural checks for glossary.md.

Usage:
    python check-glossary.py [PATH]        # defaults to ../glossary.md

Checks the mechanical conventions that are easy to break during an edit and
hard to see by reading:

    1. section headers unique and in alphabetical order
    2. the contents listing at the top agrees with the sections that exist
    3. every entry sorts under the section it sits in
    4. entries alphabetical within each section
    5. no duplicate headwords (they would collide as anchors)
    6. every internal [...](#anchor) resolves to an entry or section
    7. every external link carries the globe, per CLAUDE.md

Check 3 exists because 1 and 4 alone cannot see the failure mode that
motivated this script: moving an entry with a regex that stops at the next
`## ` steps over a `# X` section header and carries it along. The header then
sits in the wrong section and the entries it used to introduce are orphaned
under the previous letter — while an order check that resets on each header
reports success, because the misplaced header silences the comparison that
would have caught it. Anchoring each entry to its section letter is
independent of ordering, so it survives that.

Exits 1 if anything fails, so it can be wired into a hook or CI.
"""

import os
import re
import sys

# CLAUDE.md: sort by case-insensitive plain-string ordering of the entry title
# with non-alphanumerics stripped, so `co-` and `cognize` both sort under `co`.
def sort_key(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


# GitHub's anchor derivation: lowercase, drop punctuation except word chars,
# spaces and hyphens, then spaces to hyphens.
def anchor_of(title):
    return re.sub(r"[^\w\s-]", "", title.strip().lower()).replace(" ", "-")


def parse(text):
    """Return (sections, entries, toc) where entries are (title, section, lineno)."""
    sections, entries, toc = [], [], []
    section = None
    for n, line in enumerate(text.split("\n"), start=1):
        m = re.match(r"^# ([A-Z])$", line)
        if m:
            section = m.group(1)
            sections.append((section, n))
            continue
        m = re.match(r"^## (.+)$", line)
        if m:
            entries.append((m.group(1).strip(), section, n))
            continue
        # Contents listing: bare `[A](#A)` lines, or a bare letter for an
        # empty section. Only counted before the first section header.
        if section is None:
            m = re.match(r"^\[([A-Z])\]\(#([A-Z])\)$", line)
            if m:
                toc.append((m.group(1), True))
            elif re.match(r"^[A-Z]$", line):
                toc.append((line, False))
    return sections, entries, toc


def check(path):
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    sections, entries, toc = parse(text)
    fails = []

    def fail(msg):
        fails.append(msg)

    # 1. sections unique and ordered
    letters = [s for s, _ in sections]
    if len(set(letters)) != len(letters):
        dupes = sorted({s for s in letters if letters.count(s) > 1})
        fail("duplicate section headers: %s" % ", ".join(dupes))
    for (a, _), (b, n) in zip(sections, sections[1:]):
        if b <= a:
            fail("section # %s (line %d) is out of order after # %s" % (b, n, a))

    # 2. contents listing agrees with reality
    linked = {letter for letter, is_linked in toc if is_linked}
    unlinked = {letter for letter, is_linked in toc if not is_linked}
    for letter in sorted(linked - set(letters)):
        fail("contents links [%s] but there is no # %s section" % (letter, letter))
    for letter in sorted(set(letters) - linked):
        fail("# %s section exists but contents does not link it" % letter)
    for letter in sorted(unlinked & set(letters)):
        fail("contents shows %s as empty but a # %s section exists" % (letter, letter))

    # 3. every entry sorts under its own section letter
    for title, section, n in entries:
        if section is None:
            fail("entry %r (line %d) sits before any section header" % (title, n))
            continue
        key = sort_key(title)
        if key and key[0] != section.lower():
            fail("entry %r (line %d) sorts under %s but sits in # %s"
                 % (title, n, key[0].upper(), section))

    # 4. alphabetical within each section
    prev = None
    prev_section = None
    for title, section, n in entries:
        if section != prev_section:
            prev, prev_section = None, section
        key = sort_key(title)
        if prev and key < prev[0]:
            fail("entry %r (line %d) is out of order after %r" % (title, n, prev[1]))
        prev = (key, title)

    # 5. duplicate headwords collide as anchors
    seen = {}
    for title, _, n in entries:
        a = anchor_of(title)
        if a in seen:
            fail("entry %r (line %d) collides with %r on anchor #%s"
                 % (title, n, seen[a], a))
        seen[a] = title

    # 6. internal anchors resolve (entries and section headers both have them)
    known = set(seen) | {letter.lower() for letter in letters}
    for n, line in enumerate(lines, start=1):
        for a in re.findall(r"\]\(#([^)]+)\)", line):
            if a.lower() not in known:
                fail("line %d: anchor #%s does not resolve" % (n, a))

    # 7. globe convention. Mirrors the CLAUDE.md grep: the first exemption is
    # the shared repo footer, plain by cross-file convention; the second is the
    # fused link, which carries an explicit marker.
    for n, line in enumerate(lines, start=1):
        if re.search(r"\]\((?:https?:)", line):
            if "\N{GLOBE WITH MERIDIANS}" in line:
                continue
            if "is part of the" in line or "intentional: no globe" in line:
                continue
            fail("line %d: external link without the globe" % n)

    return fails


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir, "glossary.md")
    if not os.path.exists(path):
        print("no such file: %s" % path, file=sys.stderr)
        return 2
    fails = check(path)
    if fails:
        for f in fails:
            print("FAIL: %s" % f)
        print("\n%d problem(s) in %s" % (len(fails), path))
        return 1
    print("ok: %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
