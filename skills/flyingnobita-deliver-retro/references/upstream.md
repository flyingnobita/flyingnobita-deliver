# Upstream retro contract

This skill borrows the environment review from `retro` (or `mattpocock-retro`),
a user-invoked skill installed from `mattpocock/skills` and owned upstream. Step
1 runs that skill's first three steps and holds their candidates; the merged
presentation belongs to step 7 here. That borrowing assumes two things about a
file this repository does not control, so step 1 re-checks them against the
upstream `SKILL.md` it reads. This file is the record of what is relied on. A
contract change is recorded here, never by editing the upstream skill.

## What is borrowed

Steps 1 to 3: load the writing-for-agents style guide, read the primary sources
of the session, and name environment candidates. Its categories describe **one
agent's environment**: navigation, automated checks, coding standards, global
`AGENTS.md`, tool economy, no-ops, information access.

What is not borrowed is its presentation step, which this skill replaces with
step 7's single severity-ordered list.

## Check 1: the presentation boundary

Upstream must present, ask or stop the user only **after** step 3. Its
candidates must be a quiet intermediate result at the end of step 3.

A presentation, question or user stop inside steps 1 to 3 is a breach: skip it,
carry the candidates to step 7, and name the breach in the report. If upstream
has no presentation step at all, its candidates end at its last step; hold them
for step 7 the same way. Neither case is a reason to stop the retro.

## Check 2: category overlap

A category overlaps when it judges something the multi-agent [checks](checks.md)
already own:

- **Coordination** — how the orchestrator ran its agents: handoffs, report
  fidelity, dispatch hygiene, idle time, parallelism, escalation, orchestrator
  context. These are C1 to C7.
- **Role split** — which role did which work: boundary breaches, duplicated
  legwork, plan quality, test-first discipline, review yield, QA yield, profile
  fit, stop placement, gate yield. These are R1 to R9.

A finding both cover is reported once, under the retro check, with the upstream
category named in the candidate. The upstream category may still carry a finding
no C or R check covers; keep it in that case.

Renames are not overlap: an upstream category that no longer appears is replaced
by whichever new category now covers the same environment concern. Name the
replacement rather than reporting a gap. Likewise, a category this file does not
list is a stale record rather than a breach: name it in the report, and add it to
**What is borrowed** above once it is confirmed to judge one agent's environment.

## What a breach becomes

A breach is a maintenance finding, not a rework of the reviewed runs. Name it in
the report with the upstream step or category, then correct the contract here.
This file is the record, so the fix lands in this file as a dependency fix type,
never as an edit to the upstream skill. The borrowing continues: a breach
sharpens the boundary this skill applies, it does not end the dependency.
