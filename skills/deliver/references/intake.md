# Intake

## Input types

| Input | How to recognise it | Read |
|---|---|---|
| GitHub issue | URL or `#N` in the repo | `gh issue view N --comments` |
| Spec | `to-spec` (or `mattpocock-to-spec`) shape: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions; an issue or a file | The spec, plus any tickets that reference it |
| Tickets | `to-tickets` (or `mattpocock-to-tickets`) output: GitHub issues, or `.scratch/<feature>/issues/NN-*.md` files, each with "Blocked by" | Every ticket in the set and its blocking edges |
| Grill output | A `grill-with-docs` (or `mattpocock-grill-with-docs`) session's decisions in the conversation, often with `GLOSSARY.md` or ADR changes | The decisions and the docs it wrote |
| Description | Anything else written by the user | As written |

The repo's tracker convention, when `setup-matt-pocock-skills` (or `mattpocock-setup-matt-pocock-skills`) has run, is in `docs/agents/issue-tracker.md`.

An input whose structure matches no row is a description. The user's confirmation of the brief at the grilling stop catches a misread.

## Brief

Write the brief in the conversation, at most a screen:

- **Goal**: the outcome, from the user's perspective.
- **Source**: input type and links or paths.
- **Repo**: path or URL, and direct or upstream if known.
- **Scope**: what is in, and what is out.
- **Acceptance**: observable checks that prove it done.
- **Preview**: what is activated locally before the ship stage and how its state is restored, or that the user declined one.
- **Open decisions**: what the grilling round must settle.
- **Route**: single unit or ticket graph (see below).

Show the brief at the grilling stop. The user's confirmation of the brief is part of that stop.

## Grilling depth

- **Full**: issue or description. Settle the approach, test strategy, QA target, and any branch the input leaves open.
- **Gaps only**: spec, tickets, or grill output. These were already grilled when written, so ask only what is missing or contradicted by the code, plus the local preview those inputs almost never record.

## Local preview

The user may want to try the change in their own environment before it ships: an installed skill or plugin, a locally running build, a config entry. Ask at the grilling stop, for every input type and depth, whether they want one and what it covers. A preview request that arrives later adds work to the plan, which makes it a scope change.

A yes settles three things with the user, and all three go in the brief so the planner has them:

- what is activated, named by path or command (a skill directory, plugin, package, service, config entry);
- the activation command and the state it replaces, when that state is the user's own;
- how the starting state is restored, and whether the preview waits for the user to try it or restores as soon as it activates.

Activation and restore are one plan step placed before the ship stage, so no
preview work starts once shipping has begun.

## Size route

- **Single unit**: an issue, a description, or one ticket.
- **Ticket graph**: two or more tickets with blocking edges, or a spec whose tickets exist. Use the concurrency resolved by [configuration.md](configuration.md) (default 3).

A spec without tickets is a single unit when it fits one plan; otherwise propose a ticket breakdown at the plan stop. The plan stop can also turn a single unit into a ticket graph when its parts are independent and substantial.

Work too large for one run (a breakdown beyond what one orchestrator session can hold, or open decisions that need their own investigation) gets a suggestion at the grilling stop: map it first with `/wayfinder` (or `/mattpocock-wayfinder`), which only the user can start, then deliver its tickets.

## Tracker record

For an input that is not already in a tracker, settle where it is recorded at the grilling stop: direct repo, follow [project-rules.md](project-rules.md#tracker-choice); upstream repo, ask whether to open an issue there, and never record a default.
