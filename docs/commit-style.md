# Commit message style

A commit message answers *why*, not *what* — the diff already records every edited line. The message earns its place by stating the motivating problem, constraint, or goal the change serves.

**Subjects:** declarative, answering *why* the change is being made — the rationale, need, or constraint it serves. What has changed is in the change set, so doesn't need to be repeated; imperative voice (`add X`, `remove Y`) and mechanism-narrating phrases (`X directive added`, `Y section removed`) do not belong in subjects — they describe what changed, not why. Vary the framing — a log built to one template reads monotonously. Subjects from this repo that work:

- *"is_archivable must reject a run with no artefacts dir to write to"*
- *"a trailing comma keeps the transient-dir list vertical under ruff format"*
- *"commit messages should be clear and understandable with little context"*

**A subject must be understandable with little context.** Read it as someone who was not in the conversation that produced it and has not seen the diff: if you cannot tell what it is about, rewrite it. *"An honest red needs the gate in place, so the upgrade leads"* fails — it states a reason while withholding which gate, which upgrade, and which part of the repo. Name the things plainly, in the words the repo already uses for them, and leave the argument to the body.

**Bodies:** motivation first, framed around the current rationale. Don't enumerate the diff — listing every file modified or every item added repeats what the change set already shows. Brief supporting detail on mechanism is fine, but only after the why is clear.

**Format:** conventional commits — `<type>(<scope>): <subject>`.

**ADR commits:** layer the ADR status immediately after the type/scope prefix:
- `Status: Proposed` → `docs(adr): proposal: <subject>`
- `Status: Accepted` → `docs(adr): decision: <subject>`
- Other statuses (Rejected, Superseded, Deprecated) — use the status word by analogy.

**Commit proposals:** when proposing a commit for approval, always show the complete message verbatim — subject, blank line, body (if any), blank line, and trailer — exactly as it will be passed to `git commit -m`. After the message block, list the files to be staged.
