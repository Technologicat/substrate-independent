#!/usr/bin/env python3
"""Smoke tests for cc-log-extract.py.

Run as `python scripts/tests/test_cc_log_extract.py` (no dependencies) or
under pytest if it's available — both work; the file follows pytest's
discovery conventions and falls back to a tiny built-in runner.
"""

import io
import importlib.util
import json
import tempfile
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
