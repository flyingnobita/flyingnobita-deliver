# Project rules

Own repos only. Upstream repos get no rules, files, or defaults written.

## Rules file

Project rules live in the repo root's `AGENTS.md`.

- `AGENTS.md` missing: create it when the first rule is approved.
- `CLAUDE.md` present: it must be a **pointer** to `AGENTS.md`, either a symlink to it or a file whose only content is `@AGENTS.md`, optionally with a comment line. Claude Code reads `AGENTS.md` by itself only when no project `CLAUDE.md` exists. Any other `CLAUDE.md` gets a warning to the user at the grilling stop, naming what it contains; leave it unedited.

Rules go under a `## Delivery` heading in `AGENTS.md`; load `writing-for-agents` before writing them. Proposed rules are shown to the user at the grilling stop and committed on the work branch after plan approval, together with any domain docs written there.

## Merge rule

Check `AGENTS.md` for an autonomous delivery rule. If it is missing, propose this text at the grilling stop as its own yes-or-no question:

> **Autonomous delivery:** When the user starts work in this repository (an issue, spec, tickets or a description), agents may push the work branch, open a pull request, and merge it into the default branch without a further request, provided all checks pass: the full test suite, linters, the review stage, and QA when it was run. Scope changes still require the user's approval.

Write the rule only on an explicit yes to that question. A general reply to the round ("proceed", "ok", "go ahead") does not grant it: ask the question again on its own. The rule grants agents merge authority, so its consent must be unambiguous.

Until the rule is in `AGENTS.md` or explicitly approved in this run, ship this repo like an upstream repo: stop with the PR draft.

## Tracker choice

For an input that is not already in a tracker:

1. A `Tracker default` line under `## Delivery` in `AGENTS.md` decides it without asking.
2. Otherwise check whether `setup-matt-pocock-skills` has run: `docs/agents/issue-tracker.md` exists and an `## Agent skills` section is in `AGENTS.md`. If not, say once that `/setup-matt-pocock-skills` configures the tracker, and continue.
3. Ask at the grilling stop, multiple choice:
   - the configured tracker, shown only when setup has run;
   - a GitHub issue, merged into the first choice when they are the same;
   - a local file in the `.scratch/<feature>/` layout;
   - none.
4. Ask whether the answer becomes the project default. On yes, add `Tracker default: <choice>` under `## Delivery`.

Record the input in the chosen tracker before the plan stop, and reference it in the commit and PR.
