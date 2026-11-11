# Retro checks

Each check names its signal, where to look in [evidence](evidence.md), and the
usual owning file. The usual file is a starting point; the fix goes where the
origin of the rework is. Check IDs are stable: the [ledger](ledger.md) matches
recurrences by them. The seven environment categories `E1` to `E7` live in
[environment](environment.md) and join these findings in the combined report.

## Coordination

How the orchestrator ran its agents.

- **C1 Handoff gaps.** A worker asked a question, needed a follow-up, or
  explored to find something the brief or plan already held or should have
  held. Look at report `questions`, `followup_evidence` and the orchestrator's
  follow-up prompts. The fix is an item every role brief or plan carries,
  phrased as the class of information ("the fixture paths the seams use"), not
  the incident. Owner: the role brief list in `pipeline.md`, or plan
  requirements in `SKILL.md` step 4.
- **C2 Report fidelity.** A worker report disagreed with the independent run:
  claimed green but red, wrong commit, missing checks, a skipped hook. Count
  per role and profile. Owner: the report requirements in `pipeline.md`, or
  the profile.
- **C3 Dispatch hygiene.** Uncertain dispatches, prompts sent twice,
  recoveries, rejected intents, operations without results, workers or
  worktrees with no ownership decision at the end. Owner: the adapter, or a
  runtime check.
- **C4 Idle.** Time between a worker settling and the orchestrator's next
  action; runs of empty waits; workers blocked on a question while independent
  work sat ready; a user question raised mid-build that grilling could have
  asked. Owner: the adapter's wait loop, `scheduling.md`, or `intake.md`.
- **C5 Parallelism.** For a ticket graph: achieved concurrency against the
  limit, the critical path, blocking edges that were not real dependencies,
  merge conflicts, and file **overlap** between concurrent tickets (intersect
  `git diff --name-only` per ticket branch). For a single unit: independent
  parts that ran in sequence. The fix is a split rule named by the overlap's
  cause (a shared module, fixture, generated file or changelog), stating
  whether such parts stay one ticket or get an ordering edge. Owner: the split
  rule in `SKILL.md` step 4, or `scheduling.md`.
- **C6 Escalation.** Questions the orchestrator answered without a basis in
  the approved plan or a user decision (overreach), and questions it escalated
  that the plan settled (noise). Owner: `scheduling.md`.
- **C7 Orchestrator context.** Compactions, large inline tool output (full test
  logs, whole worker transcripts), and re-reading what a report already
  summarised. The orchestrator carries the run, so its window is the scarcest.
  Owner: the adapter, or the report shape in `pipeline.md`.

## Role split

Whether each piece of work landed with the right role.

- **R1 Boundary breaches.** The orchestrator edited code or tests, or debugged
  instead of dispatching; the reviewer or planner edited project files; an
  implementer pushed, changed scope or touched files outside its ticket. Match
  commits to attempts and search the orchestrator transcript for edits. Owner:
  `SKILL.md`'s role rule, or the adapter's permission mode.
- **R2 Duplicated legwork.** Two roles did the same exploration or diagnosis:
  the orchestrator re-derived what the planner found, the reviewer re-explored
  beyond the diff, the implementer re-diagnosed a planned bug. Look for the
  same files read and commands run across transcripts. Decide the one owning
  role and the artifact the others receive instead.
- **R3 Plan quality.** Plan revisions and their causes, plan claims the
  orchestrator's check refuted, seams found missing or wrong during build,
  slices reordered. Owner: `SKILL.md` step 4, or the planner profile.
- **R4 Test-first discipline.** Non-guard tests passing on the base, tests at
  seams the user did not confirm, implementation-coupled or tautological
  tests flagged in review. Owner: the build brief in `pipeline.md`.
- **R5 Review yield.** Must-fix defects found after review (by QA, the
  orchestrator, CI or the user), review iterations, a finding recurring across
  iterations, and mechanical findings a linter could own. Owner: `review.md`,
  or a repo check.
- **R6 QA yield.** QA findings a test at a seam could have caught, QA results
  contradicting the brief, and cleanup that failed to restore the starting
  state. Owner: `qa.md`, or the seams in the plan.
- **R7 Profile fit.** Per role, host, harness, model and effort: requested
  against effective settings, attempts, elapsed time, and reworks originating
  there. Effective settings come from the run's `profiles`, Herdr's startup
  inspection, Orca's `launch.requested` and `launch.effective`, or the Paseo
  agent's settings. Across the ledger, a profile whose role keeps originating
  rework needs a stronger profile or a narrower brief; one doing routine work
  with no rework can step down. Owner: the profile row in `SKILL.md` step 6's
  table for the run's host.
- **R8 Stop placement.** Each user stop and its wait time; scope changes whose
  origin is intake or grilling; decisions that reached the user late; stops
  that settled nothing. Owner: `intake.md` or `scheduling.md`.
- **R9 Gate yield.** For each gate (red check, review, QA, independent verify):
  what it caught that no earlier gate did, and its elapsed time. Across the
  ledger, report yield per gate and route. A gate that caught nothing over
  five or more runs of one route is a candidate to lighten for that route;
  Deliver runs every stage on every route, so the change is a policy decision
  for the user. A gate whose catches a cheaper earlier gate could own points
  the fix there. Owner: `pipeline.md` or `SKILL.md`.
