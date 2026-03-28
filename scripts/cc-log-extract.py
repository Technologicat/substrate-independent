#!/usr/bin/env python3
"""Extract human/assistant conversation turns from Claude Code JSONL session logs.

Usage:
    python cc-log-extract.py SESSION.jsonl [SESSION2.jsonl ...]
    python cc-log-extract.py SESSION.jsonl -o output.md
    python cc-log-extract.py SESSION.jsonl --tools full
    python cc-log-extract.py SESSION.jsonl --no-tools

Tool display modes:
    summary  (default) — one-line summary per tool call, e.g. [Read: imageview.py]
    full     — include tool input details (truncated)
    none     — omit tool calls entirely, show only prose

The output is Markdown-formatted for easy reading and further processing.
"""

import json
import sys
import argparse
from pathlib import Path


def format_tool_call(item, mode):
    """Format a tool_use content item according to the display mode."""
    if mode == "none":
        return None

    name = item.get("name", "")
    inp = item.get("input", {})

    if mode == "summary":
        # Compact one-liners for common tools
        if name in ("Read", "read"):
            fp = inp.get("file_path", "")
            return f"[Read: {Path(fp).name}]" if fp else f"[Read]"
        elif name in ("Write", "write"):
            fp = inp.get("file_path", "")
            return f"[Write: {Path(fp).name}]" if fp else f"[Write]"
        elif name in ("Edit", "edit", "MultiEdit"):
            fp = inp.get("file_path", "")
            return f"[Edit: {Path(fp).name}]" if fp else f"[Edit]"
        elif name in ("Bash", "bash"):
            cmd = inp.get("command", "")
            # First line, truncated
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

    elif mode == "full":
        inp_str = json.dumps(inp, ensure_ascii=False)
        if len(inp_str) > 200:
            inp_str = inp_str[:200] + "…"
        return f"[{name}: {inp_str}]"

    return None


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
    """Parse a JSONL session log into a list of (role, text, timestamp) tuples."""
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
                    messages.append(("HUMAN", text, timestamp))

            elif msg_type == "assistant":
                text, has_prose = extract_content(content, tool_mode)
                if text:
                    messages.append(("CC", text, timestamp))

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


def write_session(messages, label, outfile, timestamps=False):
    """Write a parsed session to the output file in Markdown format."""
    outfile.write(f"\n{'=' * 72}\n")
    outfile.write(f"## {label}\n")
    outfile.write(f"{len(messages)} turns\n")
    outfile.write(f"{'=' * 72}\n\n")

    for role, text, ts in messages:
        ts_str = f" ({format_timestamp(ts)})" if timestamps and ts else ""

        if role == "HUMAN":
            outfile.write(f"**[HUMAN]**{ts_str}:\n\n")
        else:
            outfile.write(f"**[CC]**{ts_str}:\n\n")

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
        choices=["summary", "full", "none"],
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

            write_session(messages, label, outfile, timestamps=args.timestamps)

            print(f"  → {len(messages)} turns extracted.", file=sys.stderr)
    finally:
        if args.output:
            outfile.close()


if __name__ == "__main__":
    main()
