# Native Herdr adapter

Load `herdr` and inspect the installed command groups before controlling any
pane. Use this adapter only after [host detection](../references/host-detection.md).
The initiating session remains the orchestrator with its existing settings.
Delivery needs no Herdr plugins. Initial acceptance is scoped to Claude and Codex
on North-Omarchy. Resolve the dotfiles checkout with `chezmoi source-path`
(or the known checkout if chezmoi is absent), then read
`dev-docs/plan-progress/20261022-deliver-herdr.md` there before describing this
adapter as live-validated. This evidence is not deployed into the skill tree.

## Profiles and preflight

Setup and standalone review use the purpose-specific authorization in
[run-record.md](../references/run-record.md); normal delivery retains its
brief/plan/seam approvals. Use role `smoke` for no-edit setup tasks.

Load [herdr-profiles.toml](../references/herdr-profiles.toml), project
`docs/agents/delivery.toml` if present, and explicit per-run overrides. Read the shared [configuration](../references/configuration.md) first. Extract
only planner/implementer/reviewer/qa tables for profile validation; other host
and delivery tables are not profile inputs. Each role configuration
uses role tables with `harness`, `model`, `effort`, `mode`; roles are
`planner`, `implementer`, `reviewer`, `qa`. Decode TOML with Python `tomllib` and
pass the tables as JSON `defaults`, `project`, `run` to `deliver-runtime profiles`.
It merges fields in that order and validates each whole role. Preserve requested
and effective profiles in the run. Missing required roles block setup.

The helper emits native argv, not shell command strings. Pass each argv element
separately after `agent start ... --`. It rejects provider/features without a
verified mapping, unknown fields, harnesses, modes and effort values. A parsed
model name is only requested configuration: inspect startup and effective
harness settings and establish model availability before accepting a result.
Unsupported settings go to the user; never substitute silently.

Verified CLI flag surface on 2026-10-22: Herdr 0.9.5/protocol 22, Claude Code
2.1.308 (`--model`, `--effort`, `--permission-mode`), Codex 0.163.0 (`--model`,
`-c model_reasoning_effort=...`, sandbox and approval flags); on 2026-10-28,
agy 1.4.8 (`--model`, `--effort`, `--mode`, `--dangerously-skip-permissions`;
model IDs such as `gemini-3.8-flash-high` carry the thinking tier). agy `plan`,
`auto` and `accept-edits` map to `--mode`; `dangerously-skip-permissions` maps
to its flag. Herdr launches it with `--kind agy`. Claude `plan` and
`auto` map directly; Codex `full-access` maps to its explicit bypass flag,
`auto` to workspace-write/on-request, `read-only` to read-only/on-request.
Check installed help again after upgrades. These mappings prove flag support,
not that an account can use a model. Preserve all existing integration hooks.
Require compatible client/server and current Claude/Codex integrations before
live acceptance. Refresh through `herdr integration install <kind>` only within
authorized managed-config scope, with private preimages and ownership review.

## Durable CLI contract

`deliver-runtime COMMAND` reads one JSON object on stdin and returns JSON or
`Error:` on stderr with nonzero exit. It is bundled with this skill (see
`SKILL.md`). Require it before starting. Common run input is `run_id` and optional
`state_root`. Default state is `$XDG_STATE_HOME/flyingnobita-deliver`, falling
back to `~/.local/state/flyingnobita-deliver`. Keep state outside checkouts.

| Command | Additional input and behavior |
| --- | --- |
| `create` | `repo`, `base`, `branch`, `host:{host,session,pane}`, `profiles`, optional `concurrency`, `purpose` and purpose-specific `approved` (omit before authorization). An existing branch must match the approved baseline; a new intended branch is recorded without creating it. Returns unique run ID and canonical repo/common Git directory. |
| `approve` | Purpose-specific `approved` fields from run-record.md and `evidence` of the actual request/approval. Normal delivery uses `{brief,plan,seams}` after the plan stop; never invent approval to start the planner. |
| `show` | Read persisted decisions, tasks, attempts, reports and evidence. |
| `checkpoint` | `stage`, revalidated `host:{host,session,pane}`, `evidence`. Records stage and replacement orchestrator while retaining old evidence; host/session changes are rejected. |
| `task` | Unique `task`, optional `role` (default implementer), `dependencies` naming already registered tasks. Normal delivery planners can run before plan approval; other roles follow the purpose-specific authorization in run-record.md. |
| `operation-intent` | Unique `operation_id`, `operation` (`worktree-create`, `agent-start`, `worktree-remove`, `workspace-close`), exact `target` object. Record before the corresponding Herdr mutation. Duplicate IDs fail. |
| `operation-result` | `operation_id`, observed `result` identifiers/evidence. An uncertain operation must be inspected before recording its result or attempting a different operation. |
| `attempt` | `task`, `resource:{worktree,branch,workspace,pane,agent,session}`. Validates Git identity, isolation, base, dependencies, resource collisions and the saved concurrency limit. Optional `approved_base` is an explicitly approved integration commit. Returns attempt ID and `report_path`. |
| `prompt` | `task`, `attempt`, `prompt`, `worker_session`, optional `timeout_ms` (1-60000, default 30000). Validates live pane, workspace, harness session and readiness, saves dispatch intent, then submits once through argv. Any uncertain result remains saved. Never repeat it. `herdr_bin` is a test-boundary override. |
| `dispatch-intent` | Same task/attempt and exact `prompt`; for manual dispatch after equivalent live readiness checks. Records intent only; never sends input. |
| `reconcile` | `task`, `attempt`, `observation:{session,resource,agent_state,commit,dispatch}`. Capture current host/agent inventory; helper independently checks Git/cleanliness. `dispatch` is `not-submitted` only when non-delivery is established, otherwise `uncertain`. |
| `report` | `task`, `attempt`, `report:{run_id,task,attempt,commit,checks,questions}`. Requires exact identity and current worktree HEAD, saves immutable report outside worktrees. |
| `followup` | `task`, `attempt`, `evidence` recording the plan-backed answer or user decision. From an unverified report, creates a new ready attempt with a new report path and preserves the original report. Use `prompt` once for this follow-up. It does not consume crash recovery. |
| `verify` | `task`, `attempt`, `commit`, revalidated host `session` as `host`, independent commands/results as `evidence`. Requires report without pending questions and matching HEAD. This is the orchestrator's attestation, not a test runner. |
| `recover` | `task`. Requires exited worker, proven non-submission, unchanged clean baseline and no report. Persists at most two recoveries across restarts. Completed changes require inspection/report/verification instead; ambiguity stops. |
| `cleanup-check` | `task`, `attempt`, current `observation` equal to resource, `landed` ref. Requires verified task, clean worktree and ancestry or identical landed tree (squash case). Records evidence; removes nothing itself. |

State writes are private, atomic and locked against concurrent writers. Only
the orchestrator runs state mutations; workers write their own report file.
Retain state and reports after cleanup with no automatic expiry. Never place
secrets in prompts, reports or recorded CLI responses.

## Native operations

**Fail closed:** gate delivery workspace/worker Herdr mutations on a successful `operation-intent`
write for its exact target. In a shell block, use `set -euo pipefail` and an
explicit `if` or `&&` dependency between recording and mutation. An absent
input file, rejected write or nonzero helper exit stops the mutation. After a
permission denial, rebuild and validate the intended input before continuing;
a later record is reconciliation evidence, never proof of prior intent.

1. Initialize a draft run with the known repo/base, intended branch, host binding,
   profiles and resolved `concurrency`. Record approved decisions only after their user stop. Inspect
   repo/base, worktree inventory, branch refs and destination path before
   creating anything. A pre-existing branch/path/name is a collision, even if
   Herdr would reuse it. Journal exact creation intent, then run
   `herdr worktree create --cwd REPO --branch BRANCH --base REF --path PATH --no-focus`.
   Capture `result.workspace`, `result.tab`, `result.root_pane` and actual
   worktree path; save the result before continuing. One worktree per concurrent
   ticket. Use the approved dependency frontier, the resolved concurrency limit (default three). Do not move panes.
2. Register task/attempt with returned identifiers. Journal start intent; inspect
   that the pane contains an available interactive shell. Start
   `herdr agent start NAME --kind KIND --pane PANE --timeout 30000 -- ARGV...`.
   Names are unique and at most 32 characters. Save actual harness session ID
   after readiness. agy reports its session only when it receives a prompt, so
   for `--kind agy` first record a `checkpoint` naming the pane and the fixed
   priming prompt `Reply with OK only. Do not run tools or touch files.`, send
   it once with `herdr agent prompt PANE TEXT --wait`, then read the bound
   session from `agent get PANE` and pass it as `prompt`'s `worker_session`
   (the attempt's `session` is the Herdr session). Priming grants no work; the
   task prompt still goes through `prompt`. If Herdr omits the session ID for
   any other harness, inspect the exact worker pane with its native `/status`
   diagnostic and bind the displayed session,
   effective settings and foreground process in a checkpoint. Use the manual
   `dispatch-intent` path after those equivalent live checks; keep `prompt`
   strict about its required Herdr session field. A missing or ambiguous native
   identity remains a blocker. Never infer identity from a matching cwd or a
   convenient transcript file. On startup error inspect `agent get PANE` and
   `agent read PANE --source visible`; never blindly start again.
3. Give the worker approved decisions, its allowed edits, applicable skill file
   paths, exact checks and report identity/path. For the Claude planner, keep
   `--permission-mode plan` and use its native `~/.claude/plans` output. The
   [plansDirectory setting](https://code.claude.com/docs/en/settings-reference#plansdirectory)
   rejects paths outside the project and falls back to this default; do not
   point it at the external run directory. Require the planner to name its
   actual saved plan. Copy that plan into the private run directory and record
   both paths in the matching report; the orchestrator normalizes the report
   from this saved artifact. This preserves plan-mode restrictions on project
   code. Never approve ExitPlanMode to implement.
4. Inspect visible UI and readiness before `prompt` (unknown permission dialogs
   can resemble idle). Let the helper submit once. Subsequent observation uses
   `herdr agent wait PANE --timeout 30000`, `agent get`, and `agent read`.
   Settlement alone never passes a stage: require activity/completion after the
   saved baseline, matching harness session, matching report and independent
   verification. A timeout or `agent_prompt_stalled` means inspect, not resend.
5. On `blocked` or an unfamiliar dialog, read visible UI, explain the request
   and name the exact worker/pane. Notify with
   `herdr notification show TITLE --body TEXT --sound request` and ask the user
   to answer in that pane. Preserve focus. Observe state again after the answer.
   Answer ordinary worker questions only when the approved plan settles them;
   otherwise escalate. Pause dependent work; continue independent work only when
   the answer cannot affect it.
6. On resume, revalidate host and canonical repo, read saved intents and compare
   live panes/agents/harness sessions, worktrees, refs and reports. Reuse an
   existing worker; do not dispatch it again. A vanished worker says nothing
   about changes. Retain ambiguous state. Two clear automatic recoveries are the
   limit; review/fix iterations use new tasks and are not crash recoveries.
7. Run the unchanged pipeline, QA and shipping gates. Before cleanup inspect
   current ownership (including reused/moved panes), stop only owned workers,
   re-check Git and landing, journal removal, then
   `herdr worktree remove --workspace WORKSPACE` without force. Close only owned
   remaining resources. Save the observed result and retain reports/evidence.
   Require a new ownership check immediately before every removal.

Worker completion reports and plan artifacts are mandatory here, an explicit
exception to the generic Herdr skill's terminal-first output preference.
