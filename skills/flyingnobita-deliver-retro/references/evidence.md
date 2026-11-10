# Retro evidence

Read every source read-only. Print environment variable names or hashes, never
values; transcripts and reports can hold secrets.

## Run record

State root: `$XDG_STATE_HOME/flyingnobita-deliver`, else
`~/.local/state/flyingnobita-deliver`, one directory per run ID. Find the run
for this session by matching `host.session` or `host.pane` with the executing
session (`CLAUDE_CODE_SESSION_ID`, `CODEX_THREAD_ID`, the Paseo agent ID or the
Orca runtime ID), else by `repo` and `branch`.

Read `run.json` directly. The deliver skill's `scripts/deliver-runtime.py show`
takes the run's writer lock and fails while a live orchestrator holds it; never
wait for or break the lock.

| Field | What it gives the retro |
|---|---|
| `stage`, `evidence[]` | Checkpoints and stage names in order, approvals with the user's evidence, host replacements |
| `approved` | The brief, plan and seams the roles were held to |
| `profiles` | Requested and effective role profiles |
| `concurrency` | The frontier limit to compare with achieved parallelism |
| `tasks.<id>` | Role, dependencies, `recoveries`, `verified` |
| `tasks.<id>.attempts[]` | `status`, `base`, `resource`, `prompt_sha256`, `worker_session`, `dispatch_response`, `followup_evidence`, `report_path`, effective `profile_proof` and observed transition timestamps when present |
| `operations` | Native mutations with intent and observed result; an intent without a result is an uncertain operation |
| Orca jobs | Packets, intents, receipts, settlements and `orca-verify` evidence |

Beside it: `reports/` (worker reports, plan versions, planner transcripts,
review artifacts), baseline and check logs. Herdr runs from before
2026-10-28 may also hold `dagr/run.json`, whose `events[]` carry timestamps for
`attempt_started`, `attempt_settled`, directives and notes; use them for
durations and idle gaps when present.

Prefer runtime observation timestamps when available. Inspect graph provenance
before treating its times as execution times: a backfilled collection timestamp
is not a measured start or settlement. Keep missing timings unknown and exclude
them from active-time and idle-loss totals; do not rewrite old evidence.

## Transcripts

- Orchestrator, Claude Code: `~/.claude/projects/<cwd-slug>/<session-id>.jsonl`.
- Orchestrator, Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`,
  matched by thread ID.
- Workers: the same stores, keyed by each attempt's `worker_session`. On Paseo
  use `get_agent_activity` per role agent; on Orca read native output by
  Dispatch ID through `orca-orchestration`, including archived output.

Search transcripts with targeted queries (tool names, file paths, error text)
rather than reading them whole; they are large.

## Branch history

From the delivered repo: `git log --format='%h %an %ad %s' <baseline>..<branch>`
(or the merged commit and its PR), per-ticket branches for a ticket graph, the
PR's review and CI status through `gh`, and merge conflicts recorded during
integration. Match each commit to the attempt that produced it.
