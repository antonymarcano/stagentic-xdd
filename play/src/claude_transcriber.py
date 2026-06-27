import json
import pathlib
import re
from collections import namedtuple
from datetime import datetime
from pathlib import Path

Block = namedtuple("Block", ["timestamp", "kind", "content", "body"], defaults=[""])

_RENDERERS = {
    "TOOL USE":        lambda ts, kind, c: f"`{ts}` **[{kind}]** {c}\n\n",
    "TOOL RESULT":     lambda ts, kind, c: f"`{ts}` **[{kind}]**\n\n```\n{c}\n```\n\n" if c else f"`{ts}` **[{kind}]**\n\n",
    "QUEUE OPERATION": lambda ts, kind, c: f"`{ts}` **[{kind}]** {c}\n\n",
    "ATTACHMENT":      lambda ts, kind, c: f"`{ts}` **[{kind}]** {c}\n\n",
    "AI TITLE":        lambda ts, kind, c: f"`{ts}` **[{kind}]** {c}\n\n",
}


class ClaudeTranscriber:
    def __call__(self, *, jsonl_path: Path, output_path: Path):
        output_path.write_text(_render(jsonl_path))


def _render(jsonl_path: Path):
    entries = _entries(jsonl_path)
    return f"`[VERSIONS]` Used in this run:\n```\nCLI: claude {_cli_version(entries)}\nMODEL: {_model(entries)}\n```\n" + "".join(
        map(_format, _blocks(entries))
    )


def _entries(jsonl_path):
    with pathlib.Path(jsonl_path).open() as file:
        return list(map(json.loads, file))


def _cli_version(entries):
    for entry in entries:
        if entry.get("version"):
            return entry["version"]
    return "unknown"


def _model(entries):
    for entry in entries:
        model = entry.get("message", {}).get("model")
        if model:
            return model
    return "unknown"


def _blocks(entries):
    return (
        block
        for entry in entries
        for block in _blocks_from(entry)
    )


def _blocks_from(entry):
    timestamp = _timestamp_for(entry)
    if "message" not in entry:
        block = _block_from_entry(entry, timestamp)
        return [block] if block else []
    content = entry["message"].get("content", [])
    if isinstance(content, list):
        return (_block_from_item(item, timestamp) for item in content)
    kind = entry.get("type", "").upper().replace("_", " ").replace("-", " ")
    return [Block(timestamp, kind, _strip_headings(content).strip())] if kind else []


def _timestamp_for(entry) -> str:
    return _format_time(entry.get("timestamp", ""))


def _block_from_item(item, timestamp):
    kind = item.get("type", "").upper().replace("_", " ").replace("-", " ")
    if item.get("type") == "tool_use":
        name = item.get("name", "")
        key = _tool_key(name, item.get("input", {}))
        return Block(timestamp, kind, f"{name} `{key}`")
    return Block(timestamp, kind, item.get("text") or item.get("content") or "")


def _block_from_entry(entry, timestamp):
    kind = entry.get("type", "").upper().replace("_", " ").replace("-", " ")
    if not kind:
        return None
    attachment = entry.get("attachment", {})
    added_names = attachment.get("addedNames", [])
    content = (entry.get("operation")
               or entry.get("aiTitle")
               or _strip_headings(entry.get("lastPrompt") or "")
               or entry.get("content")
               or attachment.get("type", "").replace("_", " ")
               or "")
    if entry.get("operation"):
        body = _strip_headings(entry.get("content", "")).strip()
    elif added_names:
        body = "```\naddedNames:\n" + "\n".join(added_names) + "\n```"
    else:
        body = ""
    return Block(timestamp, kind, content, body)


def _format(block):
    timestamp, kind, content, body = block
    render = _RENDERERS.get(kind)
    if render:
        result = render(timestamp, kind, content)
    else:
        result = f"`{timestamp}` **[{kind}]**\n\n{content}\n\n" if content else f"`{timestamp}` **[{kind}]**\n\n"
    return result + body + "\n\n" if body else result


def _tool_key(name, tool_input):
    key_fields = {"Bash": "command", "Read": "file_path", "Write": "file_path",
                  "Edit": "file_path", "Glob": "pattern", "Grep": "pattern"}
    field = key_fields.get(name)
    if field:
        return tool_input.get(field, "")
    return next(iter(tool_input.values()), "") if tool_input else ""


def _strip_headings(text):
    return re.sub(r'^#+ ', '', text, flags=re.MULTILINE)


def _format_time(timestamp):
    if not timestamp:
        return "NO TIMESTAMP"
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%H:%M:%SZ")
    except ValueError:
        return ""
