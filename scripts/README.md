# Scripts

Tools for working with AI pair programming session data.

## cc-log-extract.py

Extracts human/assistant conversation turns from Claude Code JSONL session logs into readable Markdown. Compresses multi-megabyte raw logs (typically 10–50 MB per session) down to something a human or LLM can read — typical compression is 100–300×.

### Usage

```bash
python cc-log-extract.py SESSION.jsonl                    # stdout, summary mode
python cc-log-extract.py SESSION.jsonl -o output.md       # write to file
python cc-log-extract.py SESSION.jsonl --tools edits      # light code review
python cc-log-extract.py SESSION.jsonl --tools full       # show tool details
python cc-log-extract.py *.jsonl -o all-sessions.md       # batch processing
python cc-log-extract.py SESSION.jsonl --timestamps       # include turn timestamps
```

### Tool display modes (`--tools`)

The main design axis: how much of CC's tool usage to preserve. Each mode targets a different reading purpose.

| Mode | Shows | Omits | Use case |
|------|-------|-------|----------|
| `summary` (default) | One-line per tool call: `[Read: app.py]`, `[Bash: git push]` | Tool input/output content | **Ethnography.** Session narrative, interaction dynamics, collaboration patterns. You see *what CC did* without *how*. |
| `edits` | Edit/Write content (diffs, new files); other tools as one-liners | File reads, tool output | **Light code review.** What actually changed, without the read/grep noise. |
| `full` | Tool input JSON (truncated at 200 chars) | Nothing (all tools shown) | **Deep review.** Debugging the AI's debugging. Understanding *why* CC made a choice. |
| `none` (`--no-tools`) | Nothing | All tool calls | **Pure dialogue.** Only human messages and CC's prose. |

### What's preserved in all modes

- All human messages, verbatim
- CC's prose (reasoning, explanations, questions) between tool calls
- Image references (as `[Image: filename]`)
- Streaming/retry deduplication (consecutive identical messages collapsed)

### What's always stripped

- Thinking blocks (CC's internal chain-of-thought)
- Tool results (the data CC got back from tools)
- Raw JSONL metadata (timestamps available via `--timestamps` flag)

### Finding session logs

Claude Code stores session logs as JSONL files. Location depends on platform:

- Linux: `~/.claude/projects/*/`
- macOS: `~/.claude/projects/*/`

Each session is a single `.jsonl` file named by session UUID. The directory name encodes the project path (with path separators replaced by hyphens).
