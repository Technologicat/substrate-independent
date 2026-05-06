#!/usr/bin/env python3
"""Extract human/assistant conversation turns from Claude Code JSONL session logs.

Usage:
    python cc-log-extract.py SESSION.jsonl [SESSION2.jsonl ...]
    python cc-log-extract.py SESSION.jsonl -o output.md
    python cc-log-extract.py SESSION.jsonl --tools full
    python cc-log-extract.py SESSION.jsonl --no-tools
    python cc-log-extract.py SESSION.jsonl --per-turn

Tool display modes:
    summary  (default) — one-line summary per tool call, e.g. [Read: imageview.py]
    edits    — show Edit/Write content (diffs, new files); other tools as
               one-liners; omit Read entirely. Light code review mode.
    full     — include tool input details (truncated)
    none     — omit tool calls entirely, show only prose

Each session header records the model that produced the assistant turns
(extracted from `message.model` in the JSONL). Single-model sessions get a
`Model: ...` line; sessions that span more than one model get a `Models: ...`
line listing each model with its CC-turn range. A `Raw model strings: ...`
line preserves the unparsed API identifiers for reproducibility — the date
suffix in those strings is the deployment date, not the model identity.

With `--per-turn`, every CC turn is also tagged inline with the API string
minus the `claude-` prefix and any date suffix (e.g. `**[CC]** *(opus-4-7)*:`).

The output is Markdown-formatted for easy reading and further processing.
"""

import json
import re
import sys
import argparse
from pathlib import Path

# Real model identifiers have shape `claude-{family}-{major}-{minor}[-{date}]`,
# e.g. `claude-opus-4-7` or `claude-opus-4-7-20260416`. The date suffix is the
# deployment date, not the model identity. Older or unfamiliar identifiers
# that don't match this shape fall through to a verbatim fallback.
_MODEL_RE = re.compile(r"^claude-(opus|sonnet|haiku)-(\d+)-(\d+)(?:-\d{8})?$")


def format_tool_call(item, mode):
    """Format a tool_use content item according to the display mode."""
    if mode == "none":
        return None

    name = item.get("name", "")
    inp = item.get("input", {})

    if mode == "summary":
        return _format_summary(name, inp)

    elif mode == "edits":
        return _format_edits(name, inp)

    elif mode == "full":
        inp_str = json.dumps(inp, ensure_ascii=False)
        if len(inp_str) > 200:
            inp_str = inp_str[:200] + "…"
        return f"[{name}: {inp_str}]"

    return None


def _truncate(s, limit):
    """Truncate string to limit, adding '…' if truncated."""
    return s if len(s) <= limit else s[:limit] + "…"


def _format_summary(name, inp):
    """Compact one-liners for all tools."""
    if name in ("Read", "read"):
        fp = inp.get("file_path", "")
        return f"[Read: {Path(fp).name}]" if fp else "[Read]"
    elif name in ("Write", "write"):
        fp = inp.get("file_path", "")
        return f"[Write: {Path(fp).name}]" if fp else "[Write]"
    elif name in ("Edit", "edit", "MultiEdit"):
        fp = inp.get("file_path", "")
        return f"[Edit: {Path(fp).name}]" if fp else "[Edit]"
    elif name in ("Bash", "bash"):
        cmd = inp.get("command", "")
        cmd_line = cmd.split("\n")[0][:120]
        return f"[Bash: {cmd_line}]"
    elif name == "Agent":
        desc = inp.get("description", "")[:100]
        return f"[Agent: {desc}]"
    elif name in ("Grep", "grep"):
        pat = inp.get("pattern", "")
        return f"[Grep: {pat}]"
    elif name in ("Glob", "glob"):
        pat = inp.get("pattern", "")
        return f"[Glob: {pat}]"
    else:
        return f"[{name}]"


def _format_edits(name, inp):
    """Edits mode: show Edit/Write content, summarize other tools, omit reads."""
    # Omit reads entirely
    if name in ("Read", "read"):
        return None

    # Edit with content
    if name in ("Edit", "edit", "MultiEdit"):
        fp = inp.get("file_path", "")
        label = Path(fp).name if fp else name
        lines = [f"[Edit: {label}]"]
        old = inp.get("old_string", "")
        new = inp.get("new_string", "")
        if old or new:
            lines.append(f"  - old: {_truncate(repr(old), 200)}")
            lines.append(f"  + new: {_truncate(repr(new), 200)}")
        return "\n".join(lines)

    # Write with content
    if name in ("Write", "write"):
        fp = inp.get("file_path", "")
        label = Path(fp).name if fp else name
        content = inp.get("content", "")
        lines = [f"[Write: {label}]"]
        if content:
            lines.append(f"  {_truncate(content, 500)}")
        return "\n".join(lines)

    # Everything else: fall back to summary one-liners
    return _format_summary(name, inp)


def _friendly_model_name(api_string):
    """Convert an API model string to a friendly form.

    `claude-opus-4-7` and `claude-opus-4-7-20260416` both → `Opus 4.7`.
    Unrecognized strings are returned unchanged — better to surface an
    unfamiliar identifier than to mangle it.
    """
    if not api_string:
        return api_string
    m = _MODEL_RE.match(api_string)
    if not m:
        return api_string
    family, major, minor = m.groups()
    return f"{family.capitalize()} {major}.{minor}"


def _per_turn_label(api_string):
    """Per-turn annotation form: API string minus `claude-` prefix and date suffix.

    `claude-opus-4-7-20260416` → `opus-4-7`. Greppable; stable across
    deployment dates. Unrecognized strings are returned lowercased but
    otherwise unchanged.
    """
    if not api_string:
        return api_string
    s = api_string.lower()
    if s.startswith("claude-"):
        s = s[len("claude-"):]
    s = re.sub(r"-\d{8}$", "", s)
    return s


def _extract_model(obj):
    """Pull the model identifier from a JSONL record, or None.

    `<synthetic>` is the harness's marker for synthesized assistant content
    (e.g. interrupted-turn placeholders) and is not a real model output;
    treat it the same as a missing field.
    """
    model = obj.get("message", {}).get("model")
    if not model or model == "<synthetic>":
        return None
    return model


def extract_content(content, tool_mode):
    """Extract readable text from a message content field.

    Returns (text, has_prose) where has_prose indicates whether
    any non-tool text was present.
    """
    if isinstance(content, str):
        return content.strip(), bool(content.strip())

    if not isinstance(content, list):
        return "", False

    parts = []
    has_prose = False

    for item in content:
        if not isinstance(item, dict):
            continue

        item_type = item.get("type", "")

        if item_type == "text":
            text = item.get("text", "").strip()
            if text:
                parts.append(text)
                has_prose = True

        elif item_type == "thinking":
            # Skip thinking blocks — internal reasoning, not conversation
            pass

        elif item_type == "tool_use":
            formatted = format_tool_call(item, tool_mode)
            if formatted:
                parts.append(formatted)

        elif item_type == "tool_result":
            # Tool results in human messages (CC's tool output fed back)
            # Usually not interesting for ethnography; skip.
            pass

        elif item_type == "image":
            source = item.get("source", {})
            if source.get("type") == "file":
                fp = source.get("file_path", "")
                parts.append(f"[Image: {Path(fp).name}]")
            else:
                parts.append("[Image]")

    return "\n".join(parts), has_prose


def parse_session(path, tool_mode="summary"):
    """Parse a JSONL session log into a list of (role, text, timestamp, model) tuples.

    `model` is the API model string for assistant turns, or None for human turns
    and for assistant turns whose model field is missing or `<synthetic>`.
    """
    messages = []

    with open(path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type")
            timestamp = obj.get("timestamp", "")
            content = obj.get("message", {}).get("content", "")

            if msg_type == "user":
                text, _ = extract_content(content, tool_mode)
                if text:
                    messages.append(("HUMAN", text, timestamp, None))

            elif msg_type == "assistant":
                text, has_prose = extract_content(content, tool_mode)
                if text:
                    messages.append(("CC", text, timestamp, _extract_model(obj)))

    return messages


def deduplicate_consecutive(messages):
    """Remove exact consecutive duplicates (same role + same text).

    CC logs sometimes repeat messages due to streaming/retry mechanics.
    """
    deduped = []
    for msg in messages:
        if deduped and deduped[-1][0] == msg[0] and deduped[-1][1] == msg[1]:
            continue
        deduped.append(msg)
    return deduped


def _model_stats(messages):
    """Compute session-level model statistics from parsed messages.

    Walks CC turns in order. Synthetic / model-less turns are transparent —
    they don't break a run, but don't contribute to it either. Returns None
    if no CC turn carries a model identifier.

    Returned dict:
      modal           — friendly name of the most-common model
      counts          — friendly name → CC-turn count
      distinct_count  — number of distinct models seen
      runs            — list of (friendly, start_cc_turn, end_cc_turn), 1-based,
                        consecutive same-model spans (synthetic gaps are bridged)
      raw             — friendly name → set of raw API strings seen
    """
    cc_turn = 0
    runs = []
    counts = {}
    raw = {}

    for role, _text, _ts, model in messages:
        if role != "CC":
            continue
        cc_turn += 1
        if not model:
            continue
        friendly = _friendly_model_name(model)
        counts[friendly] = counts.get(friendly, 0) + 1
        raw.setdefault(friendly, set()).add(model)

        if runs and runs[-1][0] == friendly:
            runs[-1] = (friendly, runs[-1][1], cc_turn)
        else:
            runs.append((friendly, cc_turn, cc_turn))

    if not counts:
        return None

    modal = max(counts, key=lambda k: counts[k])
    return {
        "modal": modal,
        "counts": counts,
        "distinct_count": len(counts),
        "runs": runs,
        "raw": raw,
    }


def _format_model_header_lines(stats):
    """Build the model-related header lines for write_session.

    Single-model session: one `Model: ...` line.
    Multi-model session: one `Models: ...` line listing each model and its
    CC-turn range(s), modal model first and tagged `(primary, N turns)`.
    Both forms are followed by a `Raw model strings: ...` line.
    """
    lines = []
    if stats["distinct_count"] == 1:
        lines.append(f"Model: {stats['modal']}")
    else:
        modal = stats["modal"]
        ordered = [modal] + [k for k in sorted(stats["counts"], key=lambda k: -stats["counts"][k]) if k != modal]
        parts = []
        for friendly in ordered:
            count = stats["counts"][friendly]
            model_runs = [r for r in stats["runs"] if r[0] == friendly]
            range_strs = [f"{s}–{e}" if s != e else str(s) for _, s, e in model_runs]
            range_part = ", ".join(range_strs)
            if friendly == modal:
                parts.append(f"{friendly} (primary, {count} turns; turns {range_part})")
            else:
                parts.append(f"{friendly} ({count} turns; turns {range_part})")
        lines.append(f"Models: {'; '.join(parts)}")

    all_raw = sorted({s for ss in stats["raw"].values() for s in ss})
    lines.append(f"Raw model strings: {', '.join(all_raw)}")
    return lines


def format_timestamp(ts):
    """Format an ISO timestamp to a readable short form."""
    if not ts:
        return ""
    # Typical format: 2026-03-27T23:45:12.345Z
    try:
        # Just date + time, no fractional seconds
        date_part = ts[:10]
        time_part = ts[11:19] if len(ts) > 19 else ts[11:]
        return f"{date_part} {time_part}"
    except (IndexError, ValueError):
        return ts


def write_session(messages, label, outfile, timestamps=False, per_turn=False):
    """Write a parsed session to the output file in Markdown format."""
    outfile.write(f"\n{'=' * 72}\n")
    outfile.write(f"## {label}\n")
    outfile.write(f"{len(messages)} turns\n")

    stats = _model_stats(messages)
    if stats:
        for line in _format_model_header_lines(stats):
            outfile.write(f"{line}\n")

    outfile.write(f"{'=' * 72}\n\n")

    for role, text, ts, model in messages:
        ts_str = f" ({format_timestamp(ts)})" if timestamps and ts else ""

        if role == "HUMAN":
            outfile.write(f"**[HUMAN]**{ts_str}:\n\n")
        else:
            model_str = f" *({_per_turn_label(model)})*" if per_turn and model else ""
            outfile.write(f"**[CC]**{model_str}{ts_str}:\n\n")

        outfile.write(text)
        outfile.write("\n\n---\n\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract conversation turns from Claude Code JSONL session logs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("files", nargs="+", help="JSONL session log file(s)")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--tools",
        choices=["summary", "edits", "full", "none"],
        default="summary",
        help="Tool call display mode (default: summary)",
    )
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Shorthand for --tools none",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Include timestamps on each turn",
    )
    parser.add_argument(
        "--per-turn",
        action="store_true",
        help="Annotate every CC turn inline with its model "
             "(e.g. **[CC]** *(opus-4-7)*:); session header is always written.",
    )

    args = parser.parse_args()
    tool_mode = "none" if args.no_tools else args.tools

    outfile = open(args.output, "w") if args.output else sys.stdout

    try:
        for filepath in args.files:
            path = Path(filepath)
            if not path.exists():
                print(f"Warning: {filepath} not found, skipping.", file=sys.stderr)
                continue

            label = path.stem
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"Processing {path.name} ({size_mb:.1f} MB)...", file=sys.stderr)

            messages = parse_session(path, tool_mode)
            messages = deduplicate_consecutive(messages)

            write_session(
                messages, label, outfile,
                timestamps=args.timestamps, per_turn=args.per_turn,
            )

            print(f"  → {len(messages)} turns extracted.", file=sys.stderr)
    finally:
        if args.output:
            outfile.close()


if __name__ == "__main__":
    main()
