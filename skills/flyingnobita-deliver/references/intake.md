# Intake

## Input types

| Input | How to recognise it | Read |
|---|---|---|
| GitHub issue | URL or `#N` in the repo | `gh issue view N --comments` |
| Spec | `to-spec` shape: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions; an issue or a file | The spec, plus any tickets that reference it |
| Tickets | `to-tickets` output: GitHub issues, or `.scratch/<feature>/issues/NN-*.md` files, each with "Blocked by" | Every ticket in the set and its blocking edges |
| Grill output | A `grill-with-docs` session's decisions in the conversation, often with `GLOSSARY.md` or ADR changes | The decisions and the docs it wrote |
| Description | Anything else written by the user | As written |

The repo's tracker convention, when `setup-matt-pocock-skills` has run, is in `docs/agents/issue-tracker.md`.

An input whose structure matches no row is a description. The user's confirmation of the brief at the grilling stop catches a misread.

## Brief

Write the brief in the conversation, at most a screen:

- **Goal**: the outcome, from the user's perspective.
- **Source**: input type and links or paths.
- **Repo**: path or URL, and own or upstream if known.
- **Scope**: what is in, and what is out.
- **Acceptance**: observable checks that prove it done.
- **Open decisions**: what the grilling round must settle.
- **Route**: single unit or ticket graph (see below).

Show the brief at the grilling stop. The user's confirmation of the brief is part of that stop.

## Grilling depth

- **Full**: issue or description. Settle the approach, test strategy, QA target, and any branch the input leaves open.
- **Gaps only**: spec, tickets, or grill output. These were already grilled when written; ask only what is missing or contradicted by the code.

## Size route

- **Single unit**: an issue, a description, or one ticket.
- **Ticket graph**: two or more tickets with blocking edges, or a spec whose tickets exist. Use the concurrency resolved by [configuration.md](configuration.md) (default 3).

A spec without tickets is a single unit when it fits one plan; otherwise propose a ticket breakdown at the plan stop. The plan stop can also turn a single unit into a ticket graph when its parts are independent and substantial.

Work too large for one run (a breakdown beyond what one orchestrator session can hold, or open decisions that need their own investigation) gets a suggestion at the grilling stop: map it first with `/wayfinder`, which only the user can start, then deliver its tickets.

## Tracker record

For an input that is not already in a tracker, settle where it is recorded at the grilling stop: own repo, follow [project-rules.md](project-rules.md#tracker-choice); upstream repo, ask whether to open an issue there, and never record a default.
