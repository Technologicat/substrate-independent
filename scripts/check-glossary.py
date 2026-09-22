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
    7. blank lines where Markdown needs them (a `---` with text directly above
       it is a setext underline, not a rule), and none between a headword and
       its first field
    8. every external link carries the globe, per CLAUDE.md
    9. the footer's "Last updated" date is current
   10. *a*/*an* before a link agrees with how the link text begins
   11. no sentence starts in lowercase, including at the start of a field or
       inside an opening quote

Checks 10 and 11 exist for the same reason as 3: each catches the residue of an
edit made somewhere else. Renaming a headword changes the first word of every
link to it, and nothing about the rename touches the article or the full stop
that sat just outside the link text. Both are scoped to what a rename can break
rather than to English at large -- a general article checker needs a
pronunciation dictionary, and this one only needs to be right about link texts.

Check 10 prints warnings for link texts it cannot judge (an acronym or a
numeral: *an LLM* and *a SQL* depend on how the reader says them). Warnings
are listed but do not fail the run.

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

import datetime
import os
import re
import subprocess
import sys

# Check 10. The default is the written first letter; these are the exceptions
# where the sound disagrees with the letter. Prefix match, lowercase.
AN_BEFORE_CONSONANT_LETTER = ("hour", "honest", "honor", "honour", "heir")
A_BEFORE_VOWEL_LETTER = ("uni", "use", "usu", "uti", "uto", "eu", "ewe",
                         "one", "once", "ubiq")

# Check 11. Abbreviations whose full stop does not end a sentence, and words
# that begin a sentence in lowercase on purpose. Two cases need no entry here:
# lowercase headwords (*co-pter*) are recognized from the file itself, and a
# field opening with a short cited term (*ptericopter*: ...) keeps the term's
# own case by lexicographic convention. A field opening with an italic
# *quotation* is a sentence, and is checked.
ABBREVIATIONS = ("e.g", "i.e", "cf", "vs", "etc", "al", "v", "n", "adj", "adv",
                 "approx", "ca", "trans")
LOWERCASE_OK = ()


# CLAUDE.md: sort by case-insensitive plain-string ordering of the entry title
# with non-alphanumerics stripped, so `co-` and `cognize` both sort under `co`.
def sort_key(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())


# GitHub's anchor derivation: lowercase, drop punctuation except word chars,
# spaces and hyphens, then spaces to hyphens.
def anchor_of(title):
    return re.sub(r"[^\w\s-]", "", title.strip().lower()).replace(" ", "-")


# Markup a reader does not see, as it can stand between a sentence boundary and
# the first letter of the next word: emphasis, quotes, the globe, link brackets.
LEAD = r"[*_\"'\u201c\u2018(\[\N{GLOBE WITH MERIDIANS}\s]*"


def expected_article(word):
    """Return "a", "an", or None when the written form cannot decide it."""
    w = word.lstrip("*_\"'\u201c\u2018(`")
    if not w:
        return None
    if w[0].isdigit() or (len(w) >= 2 and w[0].isupper() and w[1].isupper()):
        return None
    low = w.lower()
    if low.startswith(AN_BEFORE_CONSONANT_LETTER):
        return "an"
    if low.startswith(A_BEFORE_VOWEL_LETTER):
        return "a"
    return "an" if low[0] in "aeiou" else "a"


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
    warnings = []

    def fail(msg):
        fails.append(msg)

    def warn(msg):
        warnings.append(msg)

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

    # 7. blank-line structure. A `---` directly under a text line is not a
    # horizontal rule at all: Markdown reads it as a setext underline and
    # promotes the line above into a heading, so the last field of the last
    # entry in a section renders as one. Invisible in the source, obvious in
    # the render, and easy to introduce by splicing an entry in by index.
    for n, line in enumerate(lines, start=1):
        if line.strip() == "---" and n >= 2 and lines[n - 2].strip():
            fail("line %d: --- needs a blank line above it, or the line above "
                 "becomes a setext heading" % n)
        if line.startswith("## ") and n >= 2 and lines[n - 2].strip():
            fail("line %d: entry %r needs a blank line above it" % (n, line[3:]))
        if line.startswith("## ") and n >= 3 and not lines[n - 3].strip() \
                and not lines[n - 2].strip():
            fail("line %d: entry %r has two blank lines above it" % (n, line[3:]))
        if line.startswith("## ") and n < len(lines) and not lines[n].strip():
            fail("line %d: entry %r has a blank line between it and its first "
                 "field" % (n, line[3:]))

    # 8. globe convention. Mirrors the CLAUDE.md grep: the first exemption is
    # the shared repo footer, plain by cross-file convention; the second is the
    # fused link, which carries an explicit marker.
    for n, line in enumerate(lines, start=1):
        if re.search(r"\]\((?:https?:)", line):
            if "\N{GLOBE WITH MERIDIANS}" in line:
                continue
            if "is part of the" in line or "intentional: no globe" in line:
                continue
            fail("line %d: external link without the globe" % n)

    # 10. a/an before a link. The link may be italic, bold or globed.
    article_link = re.compile(
        r"(?<![\w-])(a|an|A|An)\s+[*_]*(?:\N{GLOBE WITH MERIDIANS})?\[([^\]]+)\]\(")
    for n, line in enumerate(lines, start=1):
        for m in article_link.finditer(line):
            said, text_ = m.group(1).lower(), m.group(2)
            first = text_.split()[0] if text_.split() else ""
            want = expected_article(first)
            if want is None:
                warn("line %d: '%s %s' -- cannot judge the article from the "
                     "spelling; check it by ear" % (n, m.group(1), text_))
            elif said != want:
                fail("line %d: '%s %s' should be '%s'"
                     % (n, m.group(1), text_, want if m.group(1).islower()
                        else want.capitalize()))

    # 11. lowercase sentence starts. Inline code is removed first, since a
    # full stop inside `foo.bar` ends nothing.
    lowercase_heads = tuple(t.lower() for t, _, _ in entries if t[:1].islower())
    allowed = LOWERCASE_OK + lowercase_heads

    def starts_ok(rest):
        word = re.match(r"[\w-]+", rest)
        return bool(word) and word.group(0).lower().startswith(allowed)

    sentence_start = re.compile(r"(?<!\.)([.?!])\s+" + LEAD + r"([a-z])")
    field_start = re.compile(r"^\*\*([A-Za-z][A-Za-z ]*):\*\*\s+" + LEAD + r"([a-z])")
    cited_term = re.compile(r"^\*\*[A-Za-z][A-Za-z ]*:\*\*\s+\*(?![\"\u201c*])"
                            r"([^*]{1,60})\*")
    for n, line in enumerate(lines, start=1):
        if line.startswith("**Part of speech:**"):
            continue  # grammatical notation, not prose
        plain = re.sub(r"`[^`]*`", "``", line)
        m = field_start.match(plain)
        if m:
            term = cited_term.match(plain)
            if not (term and len(term.group(1).split()) <= 4) \
                    and not starts_ok(plain[m.start(2):]):
                fail("line %d: the %s field starts in lowercase" % (n, m.group(1)))
        for m in sentence_start.finditer(plain):
            before = plain[:m.start(1)]
            prev_word = re.search(r"([\w.]+)$", before)
            if prev_word and prev_word.group(1).lower().rstrip(".") in ABBREVIATIONS:
                continue
            if starts_ok(plain[m.start(2):]):
                continue
            snippet = plain[max(0, m.start(1) - 20):m.start(2) + 20]
            fail("line %d: sentence starts in lowercase: ...%s..." % (n, snippet))

    # 9. the footer's "Last updated". This is the one line here that goes stale
    # without anybody editing it -- every other check is about something an edit
    # put on the page, and this is about an edit that failed to happen.
    #
    # Which of two questions to ask depends on whether the file is dirty, and
    # getting that backwards makes the check useless. Comparing against the last
    # *commit* alone passes while the work is still in the tree and only fails
    # afterwards -- by which point the stale footer has landed in history, which
    # is the thing this exists to prevent. So: uncommitted changes mean the file
    # is being edited now, and the footer has to say today. A clean tree is
    # merely being read, possibly at an old checkout, so the footer only has to
    # be no older than the commit it came from.
    m = re.search(r"^\*Started: [\d-]+\. Last updated: (\d{4}-\d{2}-\d{2})\.\*$",
                  text, re.MULTILINE)
    if not m:
        fail("no `*Started: ... Last updated: YYYY-MM-DD.*` footer found")
    else:
        stated = m.group(1)
        name = os.path.basename(path)
        where = os.path.dirname(os.path.abspath(path))

        def git(*args):
            try:
                return subprocess.run(("git",) + args, cwd=where, capture_output=True,
                                      text=True, timeout=10).stdout.strip()
            except (OSError, subprocess.SubprocessError):
                return ""  # no git, or no answer: nothing to compare against

        if git("status", "--porcelain", "--", name):
            today = datetime.date.today().isoformat()
            if stated != today:
                fail("footer says last updated %s, but the file has uncommitted "
                     "changes; today is %s" % (stated, today))
        else:
            committed = git("log", "-1", "--format=%cs", "--", name)
            if committed and stated < committed:
                fail("footer says last updated %s, but the file was last committed %s"
                     % (stated, committed))

    return fails, warnings


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir, "glossary.md")
    if not os.path.exists(path):
        print("no such file: %s" % path, file=sys.stderr)
        return 2
    fails, warnings = check(path)
    for w in warnings:
        print("WARN: %s" % w)
    if fails:
        for f in fails:
            print("FAIL: %s" % f)
        print("\n%d problem(s) in %s" % (len(fails), path))
        return 1
    print("ok: %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
