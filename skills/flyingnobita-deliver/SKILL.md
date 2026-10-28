---
name: flyingnobita-deliver
description: Deliver a change end to end by orchestrating agent profiles - grill, plan, test-first implementation, review, QA, then merge or open a PR. Use when the user's message starts with "deliver" or names flyingnobita-deliver, whatever the size of the work.
---

# Deliver

You are the **orchestrator**. Every delivery runs this whole workflow, however small the change: size only chooses the route in step 1, never whether to skip a stage. Text after the word "deliver" is the input.

You turn the user's input into a confirmed **brief**, run role agents through a pipeline, check every stage's result yourself, and ship. Role agents write and commit the code and tests; the only project files you edit are the rules the user approved for `AGENTS.md`, tracker records, and the domain docs from the grilling stop. You coordinate, verify, and decide what goes to the user.

**Stops** are the only points where you end your turn to wait for the user:

1. the grilling round;
2. plan approval;
3. any **scope change**: a finding that changes what is being built or why;
4. the PR draft, for an **upstream repo** only.

Work that needs steps only the user can perform (credentials, CI secrets, a third-party dashboard) is also a stop: load `mattpocock-wizard` to generate a guided script for those steps, and resume when the user reports them done.

Run everything else to completion without asking. Ending your turn is how the user is notified, so end it only at a stop, at a blocker you cannot resolve, or with the final report.

## Host adapter

Every host action below is an **operation**: start a role, send a role a follow-up, wait for an event, answer a permission, create a workspace, notify the user. Before step 1, read [host detection](references/host-detection.md), verify actual
caller/session membership, and select one adapter for the run:

- Confirmed Paseo session: [adapters/paseo.md](adapters/paseo.md).
- Confirmed Herdr session: [adapters/herdr.md](adapters/herdr.md).
- Confirmed Orca session: [adapters/orca.md](adapters/orca.md).
- Multiple confirmed hosts: ask the user to choose among them. Broken or ambiguous context: stop with the failed check.
- No adapter matches: tell the user which host you are in and stop.

The helpers `deliver-runtime` and `deliver-orca-preflight` ship with this skill as `scripts/deliver-runtime.py` and `scripts/deliver-orca-preflight.py`. Run each as `python3 <this skill's directory>/scripts/<name>.py`, wherever these references name the helper.

This skill builds on other skills and their file formats. When one is missing, or behaves differently from what [references/dependencies.md](references/dependencies.md) records, use that file's fallback and name the dependency in your report.

For configuration or legacy migration use `flyingnobita-deliver-setup`; for a
standalone branch review use `flyingnobita-deliver-review`. Questions about the
workflow use [references/workflow.md](references/workflow.md). Inspecting or
editing this skill does not start a delivery.

## 1. Intake

Read [references/intake.md](references/intake.md). Identify the input type, read it fully, and write the brief.

Done when the brief exists and its size route (single unit or ticket graph) is chosen.

## 2. Setup

1. Read [references/configuration.md](references/configuration.md) and resolve
   settings for this run. Legacy config triggers its migration path. Resolve the repository. With no local clone known, ask the user for a path and suggest any existing clones you find. For a repo not owned by `flyingnobita`, fork it as `flyingnobita` and set `upstream`. This is the only question allowed outside a stop; ask it with the grilling round when you can.
2. Classify the repo: **own repo** (owner `flyingnobita`) or **upstream repo**.
3. Own repo: read [references/project-rules.md](references/project-rules.md) and run its checks. Its questions join the grilling round.
4. Set up the work's workspace: an isolated worktree on its own branch, starting at the default branch (`origin/<default>` for an own repo, `upstream/<default>` for an upstream repo). Every role works in it, one after another.
   - **Reuse** your own workspace when the host is Paseo, the work is a single unit, and the workspace is a worktree of this repo on a non-default branch with a clean tree and no commits beyond the base ref (`git rev-list --count <base>..HEAD` is 0). Fast-forward it to the base ref.
   - Otherwise **create** one through the adapter. Herdr and Orca create isolated workspaces; Herdr treats an existing worktree as a collision. A ticket graph adds one workspace per ticket at build time ([references/pipeline.md](references/pipeline.md#ticket-graph)).
5. Record the **baseline**: install dependencies and run the full test suite and linters as the repo's own docs and config define them. A failing baseline is a blocker: report it at the grilling stop.

Done when the workspace is ready, recorded as reused or created, and the baseline result is recorded.

## 3. Grilling stop

Load `mattpocock-grilling` and grill the user on every open decision the brief leaves, at the depth intake set: for gaps-only depth, tell it to ask only what is missing or contradicted. For human steps or ticket graphs, read [references/scheduling.md](references/scheduling.md) and add its unresolved scheduling decisions. Add the setup questions and the QA offer (target host or environment, or skip) to its rounds.

Own repo: also load `mattpocock-domain-modeling`, so glossary terms and ADRs are written as decisions settle. Upstream repo: write no domain docs.

Done when every open decision is settled and the user has confirmed the brief.

## 4. Plan stop

Start the planner role, read-only, with the brief and the decisions. Its plan must name:

- the vertical **slices** of the work, in order;
- the **seams**: the public interfaces the tests go through, each with a line on what it catches and what it misses (`mattpocock-tdd` tests only at seams the user confirmed);
- the commands for the tests, the full suite and the linters.

For a single unit with **independent, substantial** parts (separate modules, no shared seams), the planner may propose them as a ticket graph with blocking edges, justifying the split against its cost: a worktree, an implementer and a merge per ticket, and a whole-branch review. The user approves the split with the plan; small or interdependent work stays one unit.

For a bug whose cause the input does not establish, the planner loads `mattpocock-diagnosing-bugs` and reproduces the bug before planning; a bug that does not reproduce is a scope change. The planner may also load `mattpocock-research` for external facts, `mattpocock-codebase-design` when the change moves a module interface, and `mattpocock-prototype` for a question code answers faster than discussion.

Read the plan yourself and check its claims against the code. Present the plan, its seams and what you verified.

Done when the user approves the plan and its seams. For a ticket graph, the plan is the ticket breakdown and its order. Then commit the approved `AGENTS.md` rules, tracker records and domain docs on the work branch with `flyingnobita-clean-commit`, before the build starts.

## 5. Build

Read [references/pipeline.md](references/pipeline.md) and run it: the implementer builds test-first at the approved seams and commits, your **red check** proves the new tests fail on the base, review loops until clean, and QA runs when offered. Answer role permission requests by the rule in the adapter. A scope change found here is a stop.

Done when every pipeline gate in `pipeline.md` has passed, each confirmed by your own run rather than a role's report.

## 6. Ship

Read [references/ship.md](references/ship.md) and follow the branch for the repo's class.

Done when the ship branch's final verification passes.

## 7. Report

End with a short report: what changed, the evidence (tests, red check, review, QA), the commit, the PR, the merged commit for an own repo, any dependency fallback used, and anything deferred. After a run with scope changes, review loops beyond the first, or fallbacks, suggest `/flyingnobita-deliver-retro` in this session. This message is the user's notification that the work is done.
