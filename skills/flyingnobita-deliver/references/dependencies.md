# Dependencies

Matt Pocock skills may be installed under their upstream names (`grilling`, `tdd`) from `mattpocock/skills` or with a local prefix (`mattpocock-grilling`, `mattpocock-tdd`). The delivery suite resolves both forms interchangeably. Where an upstream name collides with a harness built-in (such as Claude Code's `code-review`), check that the installed `SKILL.md` comes from `mattpocock/skills`. This file is the single record of what `flyingnobita-deliver` relies on from each, and the fallback when that changes. After an upstream update, check each **contract** against the dependency's current `SKILL.md`.

The pipeline follows Matt Pocock's implement workflow (`implement` / `mattpocock-implement`, `implement-spec` / `mattpocock-implement-spec`, as routed by `ask-matt` / `mattpocock-ask-matt`). If that workflow changes upstream, re-check `pipeline.md` against it.

## Skills loaded by name

| Skill | Loaded by, at | Contract | Fallback |
|---|---|---|---|
| `grilling` (or `mattpocock-grilling`) | Orchestrator, grilling stop | Settles every open decision with the user in numbered rounds, each question carrying a recommendation, and ends with a shared understanding | Run the rounds yourself: number each question, give your recommendation, ask only questions whose prerequisites are settled, and repeat until no decision is open |
| `domain-modeling` (or `mattpocock-domain-modeling`) | Orchestrator, grilling stop, direct repos | Writes resolved terms to the repo's glossary and offers ADRs only for hard-to-reverse, surprising trade-offs, following the repo's own doc-layout rules | Skip domain docs and say so in the report |
| `diagnosing-bugs` (or `mattpocock-diagnosing-bugs`) | Planner, bug with an unknown cause | Reproduces the bug and narrows it to a cause before any fix is planned | Planner reproduces the bug with a failing command or test and states the cause with evidence |
| `research` (or `mattpocock-research`) | Planner, optional | Answers a question from primary sources and saves the findings as Markdown | Planner cites the sources inline in the plan; for an upstream repo, notes go outside the repo |
| `codebase-design` (or `mattpocock-codebase-design`) | Planner, optional | Vocabulary for modules, interfaces, depth and seams | Planner describes the interface change in plain terms |
| `prototype` (or `mattpocock-prototype`) | Planner, optional | Throwaway code that answers one design question | Ask the question at the plan stop instead |
| `tdd` (or `mattpocock-tdd`) | Implementer, build | Vertical red-green slices, tests only at user-confirmed seams, its anti-patterns (implementation-coupled, tautological, horizontal slicing) | Brief the implementer with those rules directly: one failing test at an approved seam, minimal code to pass, repeat |
| `code-review` (or `mattpocock-code-review`) | Reviewer, review | Reviews `git diff <fixed-point>...HEAD` on two separate axes, Standards (documented rules plus a code-smell baseline) and Spec (missing, unrequested and wrong behaviour), without merging them | Brief the reviewer with the two axes directly, reporting each separately with file and line |
| `pr` (or `mattpocock-pr`) | Orchestrator, ship | Produces a PR body with a summary visual, before-and-after evidence, and merge danger | Write the body yourself: the repo's PR template if any, otherwise Summary, Evidence (before and after), and Notes |
| `writing-for-agents` (or `mattpocock-writing-for-agents`) | Orchestrator, `AGENTS.md` rules | Guidance for documents agents read | Write the rule as given in `project-rules.md` |
| `wizard` (or `mattpocock-wizard`) | Orchestrator, user-only steps | Generates an interactive script that walks the user through steps only they can perform | List the steps in the stop message |
| Commit capability | Implementer and orchestrator | Commits only owned changes in the repo's message style, with hooks and signing if configured | Built-in safe commit behavior (staged owned hunks, clean message, repo hooks), or a configured custom commit skill |

A skill whose name no longer loads may have been renamed upstream: look for its successor among the available skills, and record the new name here.

## Skills suggested to the user

These are user-invoked (`disable-model-invocation: true`), so the orchestrator only names them.

| Skill | When | Where |
|---|---|---|
| `/wayfinder` (or `/mattpocock-wayfinder`) | Work too large for one run | Grilling stop |
| `/flyingnobita-deliver-retro` | A run with scope changes, extra review loops, or fallbacks | Final report |

`flyingnobita-deliver-retro` loads `retro` (or `mattpocock-retro`) for its environment
categories (navigation, automated checks, coding standards, tool economy,
information access) and adds the multi-agent checks. After an upstream update
of `retro`, check that its steps 1 to 3 still end before
presenting, and that its categories do not now duplicate the retro's
[checks](../../flyingnobita-deliver-retro/references/checks.md).

## File formats read

| Producer | Format relied on | Fallback |
|---|---|---|
| `to-spec` (or `mattpocock-to-spec`) | A spec issue or file with Problem Statement, Solution and Implementation Decisions headings | Unrecognised structure is a description; the brief confirmation at the grilling stop catches misreads |
| `to-tickets` (or `mattpocock-to-tickets`) | One ticket per issue or per `.scratch/<feature>/issues/NN-*.md` file, each with a "Blocked by" field | Ask the user for the ticket order at the grilling stop |
| `setup-matt-pocock-skills` (or `mattpocock-setup-matt-pocock-skills`) | `docs/agents/issue-tracker.md` names the tracker; an `## Agent skills` section marks setup as run | Treat setup as not run, and offer GitHub, a local file, or none |

## Host dependencies

All hosts use [caller verification](host-detection.md). Paseo retains its live
profiles, MCP operations and structured permission responses. Herdr requires
the `herdr` skill, the bundled `deliver-runtime` helper, Python 3.11+
(`tomllib` for profiles), compatible native CLI and current harness integrations.
If any are missing, stop with the failed prerequisite. Herdr's
[adapter](../adapters/herdr.md) owns durable reports, plan-output capture and
recovery; its runtime helper does not grant shipping or permission authority.

Orca requires the version-matched orchestration reference, loaded either via the
`orca-orchestration` discovery stub or directly from the resolved Orca CLI with
`ORCA skills get orchestration --full` (fetching omitted references with
`ORCA skills get orchestration --reference references/<file>.md` if output is truncated).
A missing local wrapper does not block when the native full guide is available.
Executable resolution: `ORCA_CLI_COMMAND` if set, `orca-dev` in dev context,
`orca-ide` on Linux outside an Orca-managed terminal (never bare `orca` there, which starts the GNOME screen reader), otherwise `orca`.
Also requires Python 3.11+ for project TOML, `deliver-runtime` and `deliver-orca-preflight`. Its native task/dispatch
and request identities own lifecycle and recovery; the helper records delivery
evidence. Missing caller identity blocks launch. See
[the Orca adapter](../adapters/orca.md) for supported local placement and
permission limitations. Setup/review companions use the shared references,
not parallel copies of the delivery pipeline.
