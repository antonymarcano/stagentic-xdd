---
agent-directive: |
  Do not add links to files outside this repository.
  Intra-repo links are fine. External web URLs are fine.
---

> **Portability:** Do not link to files outside this repository. Intra-repo links and external web URLs are fine. Inline context rather than linking out when the content is critical to understanding the ADR.

# 0014 — Separate Claude jsonl translation from the transcriber

**Status:** Proposed

## Context

`ClaudeTranscriber` (`play/src/claude_transcriber.py`) does three jobs in one
module:

- parse a Claude session `.jsonl`;
- render the parsed entries to Markdown;
- write the Markdown to a file.

A single approval test pins the whole thing: it renders one fixture
(`sample-transcript.jsonl`) and compares the output to the committed approved
master (`sample-transcript.md`).

Adding the file to `source_paths` (ADR 0010) and running focused mutation testing
exposed the cost of that single test. Of 326 mutants, **75 survived** — and the
survivors are not spread evenly:

- **All 75 survive in the parse/translate layer** (`_block_from_entry`,
  `_block_from_item`, `_blocks_from`, `_tool_key`, `_timestamp_for`,
  `_format_time`, `_strip_headings`).
- **None survive in render** (`_format`/`_RENDERERS`) **or write** (`__call__`).

The approved master pins render and write adequately. It under-specifies
translation, because one fixture cannot reach the branches the survivors mark:
tools other than the three it uses, missing-key defaults, multi-line headings,
malformed timestamps, and the case where `_tool_key`'s dict lookup and its
fallback return the same value.

Two facts follow from where the survivors sit:

- The Claude-specific knowledge — `tool_use`/`attachment`/`aiTitle`/`lastPrompt`
  shapes, the tool→field map — is entirely in translation. It is the one part
  that is unambiguously tied to Claude's jsonl format.
- We want to transcribe sessions from more than one harness (Claude Code, Codex,
  others). Their entry labels differ. The critic evaluates a transcript by
  inference, so label *variation* is not something to design against — the
  content only needs to be present and legible.

## Decision

Replace the single `ClaudeTranscriber` with a small pipeline of named types: a
Claude-specific source, a neutral `Transcript`, a Markdown view, and a generic
orchestrator. Develop it fresh under TDD — the current coverage is too low to
refactor against safely.

### The anticipated types

We will drive the object graph using TDD, so the end result may vary but the
anticipated shape is likely to be:

- **`ClaudeJsonlSource`** (Claude-specific) — `at(path) -> Transcript`. Reads and
  parses the Claude `.jsonl` *eagerly*, so a malformed file fails at `.at(…)`,
  not later. The only part tied to Claude's jsonl format.
- **`Transcript`** (neutral) — an ordered series of `TranscriptEntry`. Knows
  nothing about Claude or Markdown.
- **`TranscriptEntry`** — one writable entry: `timestamp`, free-text `label`,
  `content`, `body`, `body_style`.
- **`MarkdownTranscript`** (generic) — `from_(transcript: Transcript)`; `str()` /
  `.render()` returns Markdown. Pure render, no IO. Reads each entry's
  `body_style`, never its `label`.
- **`Transcriber`** (generic orchestrator) — callable `(jsonl_path=,
  output_path=)`. Holds a source; per call:
  `output_path.write_text(str(MarkdownTranscript.from_(source.at(jsonl_path))))`.

### Wiring — the source is injected at the composition root

- `Transcriber` is generic; it is handed the source **class** as a factory:
  `Transcriber(ClaudeJsonlSource)`. The factory call `source.at(jsonl_path)`
  fires per run, once the path is known — `ClaudeSession` only learns the jsonl
  path at run time, so the source can't be constructed at the root.
- Duck-typed: `source` is anything with `.at(path) -> Transcript`. No protocol —
  one source means an interface would be speculative generality; it arrives with
  the second source.
- The composition roots that already name every Claude piece (`spec/conftest.py`'s
  critic branch, the integration test) swap `ClaudeTranscriber()` →
  `Transcriber(ClaudeJsonlSource)`. `ClaudeSession` is unchanged but for the
  `transcriber` type hint; `Critic` is untouched.
- `ClaudeTranscriber` is **deleted, not wrapped** — a Claude-named class that
  merely built `Transcriber(ClaudeJsonlSource)` would be pure indirection.

### Presentation styles

Each `TranscriptEntry` carries a `body_style`, reverse-engineered from current
render so output is unchanged, not invented:

- `inline` — `` `ts` **[label]** content `` (today: TOOL USE, QUEUE OPERATION,
  ATTACHMENT, AI TITLE).
- `block` — label, then content on its own line (today: USER, THINKING, TEXT,
  LAST PROMPT).
- `fenced` — content wrapped in a code fence (today: TOOL RESULT).
- an optional appended `body` (today: the `addedNames` code block).

`ClaudeJsonlSource` sets the `body_style`; `MarkdownTranscript` switches on
`body_style`, never on the label.

### Output is frozen

The pipeline must reproduce `sample-transcript.md` byte-for-byte; the approved
master is not edited. This restructure changes internal structure, not observable
output.

### Development strategy — vertical slices

With so little of the current behaviour pinned by tests, refactoring has no
safety net to lean on; the replacement is developed from the ground up using TDD.

The approach will be in slices that reads a one line transcript entry, processes that into a `Transcript` type holding the first `TranscriptEntry`, then renders out to just that one line. We will build up the style types that it handles with new fixtures until the code can achieve the same result as the current fixture.

1. **Thinnest slice** — a one-line `.jsonl` fixture for the simplest entry, end to
   end: `ClaudeJsonlSource` → a `Transcript` of one `TranscriptEntry` →
   `MarkdownTranscript` → assert it matches that line of `sample-transcript.md`.
2. **Add one entry/style per slice** — each with its own fixture, growing the
   `body_style`s and entry shapes the source handles, until the slices together
   reproduce the full `sample-transcript.md`. This drives out the 75 survivors as
   the source learns each case.
3. **Wire and swap** — assemble the callable `Transcriber`, point the composition
   roots at `Transcriber(ClaudeJsonlSource)`, and retire `claude_transcriber.py`.

### TDD discipline

Each change follows the green-step loop in
[`docs/working-practices.md`](../../working-practices.md) — focused mutmut on the
in-flight file, code dialled back until there are no survivors, commit only on
green and no survivors. The new modules go in `source_paths` and can be committed
while in flight. The point specific to this work: because every green is gated on
a clean focused run, the new code carries zero mutants by construction.

### Naming

Once complete, it will be wired into the existing codebase and `ClaudeTranscriber`
goes away. The only Claude-specific component is likely to be `ClaudeJsonlSource`;
`Transcriber`, `Transcript`, and `MarkdownTranscript` are generic. So the
`Transcriber → ClaudeTranscriber` rename is reversed — "Claude" lives only in
`ClaudeCli` and `ClaudeJsonlSource`.

## Consequences

- `ClaudeTranscriber` is replaced by small types, each with one responsibility
  and its own tests.
- A new harness costs only a new source (`…Source` with `.at(path) ->
  Transcript`); `Transcript`, `MarkdownTranscript`, and `Transcriber` are reused.
- The 75 survivors are driven out by per-case `ClaudeJsonlSource` tests the single
  approval test could not reach — translation becomes measurable, not assumed.
- No behavioural change at the boundary: the frozen approved master is the proof.
- `MarkdownTranscript` reads each entry's `body_style`, never its `label`, so
  arbitrary harness labels render uniformly — consistent with the critic
  tolerating label variation by inference.
- `ClaudeSession`/`Agent` swappability is untouched — already DI'd, deferred
  until a second session type exists.

## Alternatives considered

- **Improve coverage in place** — keep the single module, add tests to kill the
  survivors. Closes the coverage gap but leaves the module coupled to one
  provider, so the multi-harness goal stays out of reach, and the approval test
  remains an awkward vehicle for the per-case translation tests.
- **Keep `ClaudeTranscriber` as a wrapper** over `Transcriber(ClaudeJsonlSource)`
  — rejected: pure indirection with no behaviour of its own, the same layer the
  decision removes.
- **A `ClaudeTranscriptFactory` type** — rejected: in Python a class is its own
  factory (`.at` is the factory method); a separate `*Factory` adds a layer for
  nothing.
- **A source protocol / abstraction now** — rejected: one source, so an interface
  is speculative generality; it lands when a second source arrives.
- **Inject the source as a `path -> Transcript` callable** instead of the class —
  viable and looser, but puts a lambda at the root; passing the class reads
  cleanly next to `ClaudeCli`.
- **Extract-in-place, then evolve** — a structural refactor lifting the existing
  helpers into seams, then behavioural red-greens. The target design differs
  enough from the current shape that extraction would contort the old code; the
  end-to-end equivalence test supplies the net instead, so we develop fresh.
- **Fixed label vocabulary** — render total over a closed enum. Rejected: labels
  pass through from any harness, and the critic evaluates by inference, so a
  closed set adds coupling without benefit.
- **`ClaudeJsonlSource` bakes Markdown into the `Transcript`** — rejected: every
  source would re-encode the same Markdown. Keeping "what it is" in the source and
  "how it looks" in `MarkdownTranscript` lets a new source reuse rendering.
- **Ground-up rewrite that changes output / edits the approved master** —
  rejected: output is frozen to the current fixture by requirement.
