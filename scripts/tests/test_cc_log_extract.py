#!/usr/bin/env python3
"""Smoke tests for cc-log-extract.py.

Run as `python scripts/tests/test_cc_log_extract.py` (no dependencies) or
under pytest if it's available — both work; the file follows pytest's
discovery conventions and falls back to a tiny built-in runner.
"""

import contextlib
import io
import importlib.util
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SCRIPT = _HERE.parent / "cc-log-extract.py"

_spec = importlib.util.spec_from_file_location("cc_log_extract", _SCRIPT)
cle = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cle)


def test_friendly_model_name_no_date_suffix():
    assert cle._friendly_model_name("claude-opus-4-7") == "Opus 4.7"
    assert cle._friendly_model_name("claude-sonnet-4-6") == "Sonnet 4.6"
    assert cle._friendly_model_name("claude-haiku-4-5") == "Haiku 4.5"


def test_friendly_model_name_with_date_suffix():
    assert cle._friendly_model_name("claude-opus-4-7-20260416") == "Opus 4.7"
    assert cle._friendly_model_name("claude-sonnet-4-6-20260217") == "Sonnet 4.6"


def test_friendly_model_name_without_minor_version():
    # The 5 family carries no minor version; the identifier is family-major only.
    assert cle._friendly_model_name("claude-opus-5") == "Opus 5"
    assert cle._friendly_model_name("claude-sonnet-5") == "Sonnet 5"
    assert cle._friendly_model_name("claude-fable-5") == "Fable 5"
    # A dated pin of one must read its date as a date, not as a huge minor version.
    assert cle._friendly_model_name("claude-opus-5-20260101") == "Opus 5"


def test_friendly_model_name_unrecognized_returns_as_is():
    # Surface unfamiliar identifiers verbatim rather than mangle them.
    assert cle._friendly_model_name("weird-string") == "weird-string"
    assert cle._friendly_model_name("") == ""
    assert cle._friendly_model_name(None) is None


def test_per_turn_label():
    assert cle._per_turn_label("claude-opus-4-7") == "opus-4-7"
    assert cle._per_turn_label("claude-opus-4-7-20260416") == "opus-4-7"
    assert cle._per_turn_label("claude-Sonnet-4-6") == "sonnet-4-6"
    assert cle._per_turn_label("") == ""
    assert cle._per_turn_label(None) is None


def test_extract_model_filters_synthetic():
    assert cle._extract_model({"message": {"model": "<synthetic>"}}) is None
    assert cle._extract_model({"message": {"model": "claude-opus-4-7"}}) == "claude-opus-4-7"
    assert cle._extract_model({"message": {}}) is None


def test_model_stats_single_model():
    msgs = [
        ("HUMAN", "q", "t", None),
        ("CC", "a", "t", "claude-opus-4-7"),
        ("CC", "a", "t", "claude-opus-4-7"),
    ]
    stats = cle._model_stats(msgs)
    assert stats["distinct_count"] == 1
    assert stats["modal"] == "Opus 4.7"
    assert stats["counts"] == {"Opus 4.7": 2}
    assert stats["runs"] == [("Opus 4.7", 1, 2)]


def test_model_stats_multi_model_with_synthetic_bridge():
    # Synthetic turns are transparent: they bridge runs of the same model
    # rather than break them, and they don't contribute to counts.
    msgs = [
        ("HUMAN", "q", "t", None),
        ("CC", "a", "t", "claude-opus-4-6"),
        ("CC", "a", "t", "claude-opus-4-6"),
        ("CC", "a", "t", None),                # synthetic
        ("CC", "a", "t", "claude-opus-4-6"),
        ("CC", "a", "t", "claude-opus-4-7"),
        ("CC", "a", "t", "claude-opus-4-7"),
    ]
    stats = cle._model_stats(msgs)
    assert stats["distinct_count"] == 2
    assert stats["modal"] == "Opus 4.6"
    assert stats["counts"] == {"Opus 4.6": 3, "Opus 4.7": 2}
    # Synthetic at CC turn 3 is bridged: Opus 4.6 spans 1–4.
    assert stats["runs"] == [("Opus 4.6", 1, 4), ("Opus 4.7", 5, 6)]


def test_model_stats_no_models_returns_none():
    msgs = [
        ("HUMAN", "q", "t", None),
        ("CC", "a", "t", None),
    ]
    assert cle._model_stats(msgs) is None


def test_format_model_header_single_model():
    stats = cle._model_stats([("CC", "a", "t", "claude-opus-4-7")])
    assert cle._format_model_header_lines(stats) == [
        "Model: Opus 4.7",
        "Raw model strings: claude-opus-4-7",
    ]


def test_format_model_header_multi_model_modal_first():
    msgs = [
        ("CC", "a", "t", "claude-opus-4-7"),
        ("CC", "a", "t", "claude-opus-4-6"),
        ("CC", "a", "t", "claude-opus-4-6"),
        ("CC", "a", "t", "claude-opus-4-6"),
    ]
    stats = cle._model_stats(msgs)
    lines = cle._format_model_header_lines(stats)
    # Modal model (Opus 4.6, 3 turns) listed first with "primary" tag.
    assert lines[0].startswith("Models: Opus 4.6 (primary, 3 turns;")
    assert "Opus 4.7" in lines[0]
    assert lines[1] == "Raw model strings: claude-opus-4-6, claude-opus-4-7"


@contextlib.contextmanager
def pinned_tz(name):
    """Run the block with the process timezone pinned to `name`.

    `TZ` + `tzset` is process-global, so it is restored on the way out —
    including the case where `TZ` was unset to begin with.
    """
    previous = os.environ.get("TZ")
    os.environ["TZ"] = name
    time.tzset()
    try:
        yield
    finally:
        if previous is None:
            del os.environ["TZ"]
        else:
            os.environ["TZ"] = previous
        time.tzset()


def test_format_timestamp_preserves_the_instant():
    # Whatever zone the machine running this is in, the rendered time has to denote
    # the moment the log recorded. Parsing it back is the form of the check that
    # survives being run anywhere.
    rendered = cle.format_timestamp("2026-03-27T23:45:12.345Z")
    parsed = datetime.strptime(rendered, "%Y-%m-%d %H:%M:%S %z")
    assert parsed == datetime(2026, 3, 27, 23, 45, 12, tzinfo=timezone.utc)


def test_format_timestamp_is_local_and_may_cross_the_date_line():
    if not hasattr(time, "tzset"):  # Windows: no way to pin the zone
        return
    with pinned_tz("Europe/Helsinki"):
        # 22:22 UTC is already the next day locally — the case that decides which
        # month a boundary session belongs to.
        assert cle.format_timestamp("2026-06-05T22:22:11.000Z") == "2026-06-06 01:22:11 +03:00"
        # Same input clock time in winter: one hour less offset, so 00:22 not 01:22.
        assert cle.format_timestamp("2026-01-05T22:22:11.000Z") == "2026-01-06 00:22:11 +02:00"
    with pinned_tz("UTC"):
        assert cle.format_timestamp("2026-06-05T22:22:11.000Z") == "2026-06-05 22:22:11 +00:00"


def test_format_timestamp_degenerate_inputs():
    assert cle.format_timestamp("") == ""
    # Verbatim beats a guess: an unrecognized stamp is still evidence of something.
    assert cle.format_timestamp("not a timestamp") == "not a timestamp"
    if not hasattr(time, "tzset"):
        return
    with pinned_tz("Europe/Helsinki"):
        # No zone in the input: the log format specifies UTC, so read it as UTC
        # rather than as whatever the reading machine happens to be set to.
        assert cle.format_timestamp("2026-06-05T22:22:11") == "2026-06-06 01:22:11 +03:00"


def test_end_to_end_parse_and_write():
    fixture = [
        {"type": "user", "timestamp": "2026-05-07T10:00:00Z",
         "message": {"content": "hello"}},
        {"type": "assistant", "timestamp": "2026-05-07T10:00:01Z",
         "message": {"model": "claude-opus-4-7",
                     "content": [{"type": "text", "text": "hi back"}]}},
        {"type": "assistant", "timestamp": "2026-05-07T10:00:02Z",
         "message": {"model": "claude-opus-4-7",
                     "content": [{"type": "text", "text": "more"}]}},
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for obj in fixture:
            f.write(json.dumps(obj) + "\n")
        path = Path(f.name)

    try:
        msgs = cle.parse_session(path)
        assert len(msgs) == 3
        assert msgs[0][0] == "HUMAN"
        assert msgs[0][3] is None
        assert msgs[1] == ("CC", "hi back", "2026-05-07T10:00:01Z", "claude-opus-4-7")

        out = io.StringIO()
        cle.write_session(msgs, "fixture", out)
        text = out.getvalue()
        assert "Model: Opus 4.7" in text
        assert "Raw model strings: claude-opus-4-7" in text
        assert "**[HUMAN]**:" in text
        assert "**[CC]**:" in text

        out = io.StringIO()
        cle.write_session(msgs, "fixture", out, per_turn=True)
        assert "**[CC]** *(opus-4-7)*:" in out.getvalue()
    finally:
        path.unlink()


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
