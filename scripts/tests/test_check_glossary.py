#!/usr/bin/env python3
"""Tests for check-glossary.py.

Run as `python scripts/tests/test_check_glossary.py` (no dependencies) or
under pytest if it's available — both work; the file follows pytest's
discovery conventions and falls back to a tiny built-in runner.

Most tests build a small synthetic glossary rather than editing the real one.
A test that finds its bug by matching a sentence in glossary.md breaks the
next time that sentence is edited, which is the failure mode the checker
itself exists to catch. The one exception is the last test, which asks only
that the real file passes.

The bug tests are reconstructions of slips that reached the repository:
each one passed every check that existed at the time.
"""

import importlib.util
import os
import shutil
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SCRIPT = _HERE.parent / "check-glossary.py"
_GLOSSARY = _HERE.parent.parent / "glossary.md"

_spec = importlib.util.spec_from_file_location("check_glossary", _SCRIPT)
cg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cg)


# A well-formed miniature: contents listing, three sections, footer. Each test
# swaps one line for a broken one. Kept outside any git repository by running
# from a temporary directory, so the footer check has no history to compare
# against and stays out of the way.
_BASE = """# Field Guide to Useful Neologisms

A test glossary.

[A](#A)
[C](#C)
[L](#L)
[S](#S)

---

# A

## Aria-worthy design
**Meaning:** Clearing the bar the project has already set.  
**Usage:** *"Aria-worthy design is only a partial True Name."*  
**Context:** Scoping decisions.

---

# C

## Cognize
**Part of speech:** v. trans. (with derivatives *cognic*, adj.)  
**Meaning:** To know.  
**Context:** Philosophy.

## co-pter
**Meaning:** The thing that is dual to flying.  
**Extension:** *ptericopter*: a thing that both flies and is a co-pter.  
**Context:** Etymology.

---

# L

## Lateral glance
**Meaning:** A frequent target of the glance is a *[snowball effect](#snowball-effect)* in the making.  
**Connections:** Pairs with *[co-pter](#co-pter)*. *[co-pter](#co-pter)* is lowercase by design.  
**Context:** Maintenance.

---

# S

## Snowball effect
**Meaning:** A small task expands through revealed coupling.  
**Context:** Feature work.

---

*Started: 2026-01-01. Last updated: 2026-01-01.*
"""


def _check(text):
    """Run the checker on `text` in a scratch directory; return (fails, warnings)."""
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "glossary.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return cg.check(path)
    finally:
        shutil.rmtree(tmp)


def _swap(old, new):
    assert _BASE.count(old) == 1, "fixture drifted: %r" % old
    return _BASE.replace(old, new, 1)


def _one_failure(fails, *fragments):
    assert len(fails) == 1, "expected one failure, got %r" % fails
    for fragment in fragments:
        assert fragment in fails[0], "%r not in %r" % (fragment, fails[0])


def test_base_fixture_passes():
    fails, warnings = _check(_BASE)
    assert fails == [], fails
    assert warnings == [], warnings


# --- the historical bugs ------------------------------------------------------

def test_article_left_behind_by_rename():
    # "an *Inevitable Snowball Effect*" became "an *snowball effect*" when the
    # headword was renamed: the rename touched the link text, not the article.
    fails, _ = _check(_swap("is a *[snowball effect]", "is an *[snowball effect]"))
    _one_failure(fails, "'an snowball effect'", "should be 'a'")


def test_lowercase_link_after_full_stop():
    # A sentence opening on a link whose text was written in lowercase.
    fails, _ = _check(_swap("*[co-pter](#co-pter)* is lowercase by design.",
                            "*[aria-worthy design](#aria-worthy-design)* is a partial True Name."))
    _one_failure(fails, "sentence starts in lowercase", "aria-worthy")


def test_lowercase_inside_opening_quote():
    # The same slip in a Usage quotation, where no full stop precedes it:
    # a scan for lowercase after full stops walked straight past this one.
    fails, _ = _check(_swap('*"Aria-worthy design is', '*"aria-worthy design is'))
    _one_failure(fails, "the Usage field starts in lowercase")


def test_blank_line_between_headword_and_first_field():
    fails, _ = _check(_swap("## Snowball effect\n**Meaning:**",
                            "## Snowball effect\n\n**Meaning:**"))
    _one_failure(fails, "'Snowball effect'", "blank line between it and its first field")


# --- what must *not* fail -----------------------------------------------------

def test_acronym_warns_but_passes():
    # *an LLM* or *a LLM* depends on the reader; the checker says so and moves on.
    fails, warnings = _check(_swap("is a *[snowball effect]", "is an *[LLM snowball effect]"))
    assert fails == [], fails
    assert len(warnings) == 1 and "check it by ear" in warnings[0], warnings


def test_cited_term_keeps_its_own_case():
    # *ptericopter* opens its field in lowercase because it is a word cited as
    # a word. The base fixture already contains it; this pins that it passes.
    fails, _ = _check(_BASE)
    assert not any("Extension" in f for f in fails), fails


def test_part_of_speech_notation_is_not_prose():
    # "v. trans. (with derivatives" is grammatical shorthand, not a sentence.
    fails, _ = _check(_BASE)
    assert not any("with derivatives" in f for f in fails), fails


def test_lowercase_headword_may_start_a_sentence():
    # *co-pter* is lowercase by design, so a sentence may open on it.
    fails, _ = _check(_BASE)
    assert not any("co-pter" in f for f in fails), fails


# --- the article rules, directly ----------------------------------------------

def test_expected_article():
    cases = {
        "snowball": "a", "aria-worthy": "an", "hammerspace": "a",
        "umbrella": "an", "owl": "an",
        # silent h
        "hour": "an", "honest": "an", "heir": "an",
        # vowel letter, consonant sound
        "university": "a", "user": "a", "one-off": "a", "euphemism": "a",
        # undecidable from spelling
        "LLM": None, "SQL": None, "OS-tan": None, "8-bit": None,
        # a capital alone is not an acronym
        "Co-pter": "a",
    }
    wrong = {w: (want, cg.expected_article(w)) for w, want in cases.items()
             if cg.expected_article(w) != want}
    assert not wrong, wrong


# --- the real file ------------------------------------------------------------

def test_real_glossary_passes():
    # Copied out of the repository so the footer check doesn't depend on
    # whether the working tree happens to be dirty when the tests run.
    with open(_GLOSSARY, encoding="utf-8") as f:
        fails, _ = _check(f.read())
    assert fails == [], fails


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed.")
    raise SystemExit(0 if failed == 0 else 1)
