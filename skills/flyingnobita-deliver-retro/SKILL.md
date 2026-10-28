---
name: flyingnobita-deliver-retro
description: Run a retrospective on one or more flyingnobita-deliver runs and propose improvements to the delivery skill, its runtime checks and role profiles.
disable-model-invocation: true
---

# Delivery retrospective

The user has asked for a **retrospective** on delivery work. It extends
`mattpocock-retro`, which reviews one agent's environment, with the layer a
multi-agent run adds: **coordination** (how the orchestrator ran its agents)
and **role split** (whether each piece of work landed with the right role). You
propose the smallest change to the delivery system that prevents each loss of
time, quality or authority next run, and track whether past fixes held.

The retro is read-only toward deliveries. It mutates no run record, pane,
worker, worktree or branch. Its only writes are its own [ledger](references/ledger.md)
entries, and it edits skills or code only after the user picks candidates.

## Steps

1. Load `mattpocock-retro` with the Skill tool. If the harness refuses it
   because it is user-invoked, read `~/.agents/skills/mattpocock-retro/SKILL.md`
   instead. Run its steps 1 to 3 on the orchestrator's session and the
   delivered repo; hold its candidates for step 7 here rather than presenting
   them now. If neither load works, load `mattpocock-writing-for-agents` and
   name the missing dependency in the report.

2. Resolve the runs. Default to the run this session orchestrated; otherwise
   the run ID, repo or branch the user names. "Recent runs" or a trend request
   means every run in the state root for the named repo, newest first. Read
   [evidence](references/evidence.md) and collect each run's primary sources,
   then read the [ledger](references/ledger.md) for past retros and their fixes.
   Done when each run's record, reports, branch history and orchestrator
   transcript are located, or each missing one is named with the reason.

3. Build a **timeline** per run: stages and user stops, then every task and
   attempt with its role, effective profile, start, settlement, report, verify
   result, follow-ups and recoveries. Done when every attempt in the run record
   appears on the timeline with an outcome.

4. Mark every **rework**: a plan revision, an attempt beyond a task's first, a
   review iteration beyond the first, a failed gate, a scope change, a worker
   report the independent run contradicted, and any correction the orchestrator
   or user made to a role's output. Trace each to its **origin**: the earliest
   stage and role that had the information to prevent it. Done when every rework
   has an origin, or is marked unattributable with the reason.

5. Run every check in [checks](references/checks.md) against the timeline and
   reworks. These are the multi-agent checks `mattpocock-retro` lacks; a
   finding both cover is reported once, here. Done when every check ID has a
   finding or an explicit "clean, with evidence".

6. Turn findings into candidates, using the ledger's history:
   - A finding matching a past candidate (same check ID and owning file) is a
     **recurrence**. If that candidate was implemented, its fix did not hold:
     raise its severity one level and step its fix type up the ladder below.
   - An implemented past candidate whose measure the new runs satisfy has
     **held**; report it in one line.

   Choose the strongest **fix type** that removes the finding, in this order:
   1. **Runtime check**: a deterministic refusal in `deliver-runtime` or
      `deliver-orca-preflight` (the deliver skill's `scripts/`), with a test in
      `scripts/common/tests/`. Use for a **mechanical** finding (a missing
      field, an unverified state passing a gate, a duplicate dispatch) that
      recurs, or whose first occurrence passed a gate. The candidate states the
      refusal condition, the command that refuses, a test case built from this
      run's evidence, and any legitimate run it could wrongly refuse.
   2. **Skill text**: a sharper step, completion criterion or role brief in the
      file that owns the behaviour (table below). The default for a first
      mechanical finding that passed no gate.
   3. **Profile**: a role's harness, model, effort or mode.
   4. **Project rule**: the delivered repo's `AGENTS.md` `## Delivery` section,
      `docs/agents/delivery.toml`, or a repo check from step 1.
   5. **Dependency**: an upstream `mattpocock-*` skill; record the contract
      change in `references/dependencies.md`.

   | Behaviour | Owning file under `dot_agents/skills/flyingnobita-deliver/` |
   |---|---|
   | Stops, stage order, orchestrator vs role edits, ticket split rule | `SKILL.md` |
   | Brief, grilling depth, size route | `references/intake.md` |
   | Role briefs, build and red-check gates, ticket graph merges | `references/pipeline.md` |
   | Review classification and repair loop | `references/review.md` |
   | Frontier, questions, human work, partial runs | `references/scheduling.md` |
   | QA guardrails and method | `references/qa.md` |
   | Landing and publication | `references/ship.md` |
   | Concurrency, landing and role settings | `references/configuration.md` |
   | Native operations, waits, permissions, recovery | `adapters/<host>.md` |
   | Herdr default profiles | `references/herdr-profiles.toml` |
   | Paseo shared profiles | `.chezmoidata/paseo.json` (repo root) |
   | Orca role profiles | the delivered repo's `docs/agents/delivery.toml` `[hosts.orca.roles.<role>]`, changed through `flyingnobita-deliver-setup` |

   Done when every candidate names one fix type, one owning file and a
   **measure**: the observable in the next run's evidence that shows it worked.

7. Present the candidates in severity order:
   1. **Authority**: a gate passed on unverified evidence, a role or the
      orchestrator acted beyond its approval, or a stop was skipped.
   2. **Correctness**: a defect shipped, or was caught only by QA, CI or the
      user.
   3. **Rework**: loops and revisions, ranked by elapsed time lost.
   4. **Waste**: idle time, duplicated legwork, oversized context.

   Give each candidate as: title; check ID; evidence (run ID, attempt or report
   path, timestamp or transcript line); origin; recurrence count; fix type and
   owning file with the proposed wording or check; measure. Merge the held
   `mattpocock-retro` candidates into the same order, labelled by their
   category. Then give the trends from the ledger: recurring findings, fixes
   that held, and the gate yield and profile fit tables from checks R7 and R9.
   End with the clean checks in one line.

8. Write this retro's ledger entry, with every candidate `proposed`. Done when
   the entry exists and the user has the candidate list.

When the user picks candidates, update their ledger status. Implement picked
candidates in the dotfiles source under `dot_agents/skills/` or
`scripts/common/`, or the delivered repo for project rules, with a CHANGELOG
entry, commit with `flyingnobita-clean-commit`, and record the commit in the
ledger. Deployment is a separate publish request.
