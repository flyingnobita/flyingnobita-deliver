# Native Herdr adapter

Load `herdr` and inspect the installed command groups before controlling any
pane. Use this adapter only after [host detection](../references/host-detection.md).
The initiating session remains the orchestrator with its existing settings.
Delivery needs no Herdr plugins. Initial acceptance is scoped to Claude and Codex
on Linux. Omp and OpenCode passed bounded native no-edit smokes on
2026-10-30; neither establishes a complete delivery cycle. For OpenCode,
full-TUI session-bound launch is required; headless/mini mode does not run the
native reporter. Do not claim platform or live compatibility beyond checked
evidence.

## Profiles and preflight

Setup and standalone review use the purpose-specific authorization in
[run-record.md](../references/run-record.md); normal delivery retains its
brief/plan/seam approvals. Use role `smoke` for no-edit setup tasks.

Load [herdr-profiles.toml](../references/herdr-profiles.toml) as `defaults` and
read the project layer from `[hosts.herdr.roles.<role>]` tables in the project's
`docs/agents/delivery.toml`. Decode TOML with Python `tomllib` and send the
parsed document to `deliver-runtime herdr-project-roles`; it returns the
`roles` project layer, the detected `layout` and any `warning`. Show a warning
to the user. A file with only old top-level `[planner]`, `[implementer]`,
`[reviewer]` and `[qa]` tables and no `[hosts.herdr.roles.*]` still yields the
same project layer, with a warning that the layout is outdated and that
`deliver-setup` (or `flyingnobita-deliver-setup`) moves the tables. Read the shared
[configuration](../references/configuration.md) first. Extract only
planner/implementer/reviewer/qa tables for profile validation; other host and
delivery tables are not profile inputs. Each role configuration uses role tables
with `harness`, `model`, `effort`, `mode`; roles are `planner`, `implementer`,
`reviewer`, `qa`. Pass the tables as JSON `defaults`, `project`, `run` to
`deliver-runtime profiles`. It merges fields in that order and validates each
whole role. Preserve requested and effective profiles in the run. Missing
required roles block setup.

The helper emits native argv, not shell command strings. OpenCode first returns
`argv: null` pending a matching native session; follow
[OpenCode launch](../references/opencode-launch.md) before startup. Once bound,
pass each argv element separately after `agent start ... --`. It rejects provider/features without a
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
Pi is supported for all four roles: `effort` maps to `--thinking`, `model` to
`--model` (provider-qualified, such as `opencode-go/kimi-k3.1-pro`), and
`mode = "default"` adds no permission flags. Pi uses its native tools and
approval behavior; this mode provides no sandbox or read-only guarantee, so a
planner's or reviewer's read-only behavior is a role contract. Launch with
`--kind pi`. These flags were checked against installed `pi --help` on
2026-10-29; a complete Herdr delivery cycle with Pi remains unverified. Require
the same readiness and worker-session checks below.

omp 18.13.3 on 2026-10-30 supports all four roles: `model` maps to `--model`,
`effort` to `--thinking` (`off`, `minimal`, `low`, `medium`, `high`, `xhigh`,
`max`, `auto`), and `mode` to `--approval-mode` (`always-ask`,
`always-ask-cached`, `write`, `yolo`), verified space-separated against
installed help. These modes are omp's own approval policy, not sandboxing, and
`write` and `yolo` reduce prompts. `mode = "default"` adds no flag and inherits
the host's configured approval behavior, so it is not an approval guarantee.
No sandbox or read-only enforcement exists: a planner's or reviewer's read-only
behavior is a role contract. Launch with `--kind omp`, which `agent start --help`
lists. On 2026-10-30, current integration v10 and omp 18.14.0 passed the
bounded native no-edit smoke on Linux with DeepSeek V4 Flash/high,
matching session and observed working/done. A complete delivery cycle remains
unverified; check current integration status before each new run.

OpenCode 2.2.2 uses a fresh native session to select explicit model/variant,
then full-TUI argv `--session <ID>`; the root command has no model/variant flags.
The [OpenCode launch branch](../references/opencode-launch.md) defines the
session request, journal, native receipt and profile binding. `mode = "default"`
is the only supported mode, preserving native approvals. Model variants are
provider-defined and must be available and observed at startup. No sandbox or
read-only enforcement exists: planner/reviewer behavior remains a role contract.
V2 Mini/headless reporting is unsupported upstream; neither Mini nor
`--standalone` supplies a substitute for the full TUI. On Linux the
corrected path reported the exact session, working and done, with no tools or
edits. A complete OpenCode delivery cycle remains unverified.

Check installed help again after upgrades. These mappings prove flag support,
not that an account can use a model. Preserve all existing integration hooks.
Require compatible client/server and a current integration for every planned
harness before live acceptance. Refresh through `herdr integration install
<kind>` only within authorized managed-config scope, with private preimages and
ownership review.

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
| `checkpoint` | `stage`, revalidated `host:{host,session,pane}`, `evidence`. Records stage and replacement orchestrator while retaining old evidence. A host change is rejected. A session change, such as a restarted orchestrator, needs `session_change:{caller_evidence,user_confirmation}`: Herdr's caller check proving the new session and the user's confirmation. Existing attempts keep working; new attempts must use the new session. Never create a new run only because the session changed. |
| `task` | Unique `task`, optional `role` (default implementer), `dependencies` naming already registered tasks. Normal delivery planners can run before plan approval; other roles follow the purpose-specific authorization in run-record.md. |
| `operation-intent` | Unique `operation_id`, `operation` (`worktree-create`, `agent-start`, `worktree-remove`, `workspace-close`), exact `target` object. Record before the corresponding Herdr mutation. Duplicate IDs fail. |
| `operation-result` | `operation_id`, observed `result` identifiers/evidence. An uncertain operation must be inspected before recording its result or attempting a different operation. |
| `attempt` | `task`, `resource:{worktree,branch,workspace,pane,agent,session}`. Validates Git identity, isolation, base, dependencies, resource collisions and the saved concurrency limit. Optional `approved_base` is an explicitly approved integration commit. Returns attempt ID and `report_path`. |
| `worktree-trust` | `task`, `attempt`, the attempt's planned profile `harness`, `method` (`harness-config`, `native-flag`, `operator-accepted`, `not-required`), `trusted_path` resolving to the attempt worktree, and observed `evidence`. Append-only per checkout and harness; `prompt` and `dispatch-intent` refuse without a matching record. |
| `profile-bind` | `task`, `attempt`, observed profile, actual harness session and availability/startup evidence. Records immutable per-attempt proof; [profile-proof.md](../references/profile-proof.md) defines authorized overrides. |
| `prompt` | `task`, `attempt`, `prompt`, `worker_session`, optional `timeout_ms` (1-60000, default 30000). Requires the recorded worktree trust, then validates live pane, workspace, harness session and readiness, saves dispatch intent, then submits once through argv. Waits for `working` or `blocked` acknowledgement, not task completion. Any uncertain result remains saved. Never repeat it. `herdr_bin` is a test-boundary override. |
| `dispatch-intent` | Same task/attempt and exact `prompt`, plus the recorded worktree trust; for manual dispatch after equivalent live readiness checks. Records intent only; never sends input. |
| `reconcile` | `task`, `attempt`, `observation:{session,resource,agent_state,commit,dispatch}`. Capture current host/agent inventory; helper independently checks Git/cleanliness. `dispatch` is `not-submitted` only when non-delivery is established, otherwise `uncertain`. |
| `report` | `task`, `attempt`, `report:{run_id,task,attempt,commit,checks,questions}`. Requires exact identity and current worktree HEAD, saves immutable report outside worktrees. |
| `followup` | `task`, `attempt`, `evidence` recording the plan-backed answer or user decision. From an unverified report, creates a new ready attempt with a new report path and preserves the original report. Use `prompt` once for this follow-up. It does not consume crash recovery. |
| `verify` | `task`, `attempt`, `commit`, revalidated host `session` as `host`, independent commands/results as `evidence`. Requires report without pending questions and matching HEAD. This is the orchestrator's attestation, not a test runner. |
| `handoff` | `task`, `attempt`, `evidence` (handoff document or the observed reason, such as a quota refusal), optional `worker:{workspace,pane,agent}`, optional `requested_profile` with `profile_authorization`. For an unreported attempt whose worker cannot continue, or whose prompt arrived but never ran. Requires a `reconcile` matching the current HEAD and cleanliness. Moves the work, partial commits included, to a new ready attempt in the same worktree; the old attempt stays `handed-off`. Use `prompt` once for the new attempt. After a report, use `followup` instead. |
| `abandon` | `task`, `evidence`, `user_decision`. Closes an unverified task the user chose to drop. Releases its worktree and pane for other tasks; dependents stay blocked. Removes nothing. |
| `wait` | `task`, `attempt`, optional `timeout_s` (at most 600, default 300), `poll_s`, `busy_pattern`. Read-only. Returns `reported`, `blocked`, `exited`, `background-running` (pane idle, but a matching process such as a test still runs in the worktree), `settled-no-report` or `timeout`. Never matches its own process. `herdr_bin` is a test-boundary override. |
| `recover` | `task`. Requires exited worker, proven non-submission, unchanged clean baseline and no report. Persists at most two recoveries across restarts. Completed changes require inspection/report/verification instead; ambiguity stops. |
| `cleanup-check` | `task`, `attempt`, current `observation` equal to resource, `landed` ref. Requires verified task, clean worktree and ancestry or identical landed tree (squash case). Records evidence; removes nothing itself. |

State writes are private, atomic and locked against concurrent writers. Only
the orchestrator runs state mutations; workers write their own report file.
Retain state and reports after cleanup with no automatic expiry. Never place
secrets in prompts, reports or recorded CLI responses.

New runs require implementer `test_scope`/`test_evidence` reports and independent
`test_results` at verification. Read the [test evidence contract](../references/test-evidence.md)
for the exact fields, exemptions and historical-run compatibility. Dispatch
acknowledgement, including `blocked`, grants no completion or verification.

Use `profile-bind` with `observed_profile`, `worker_session`,
`availability_verified: true` and retained startup `evidence` before verification.
Read [effective profile proof](../references/profile-proof.md) for exact fields,
authorized quota switches and historical-run compatibility.

## Compact observation and progress

On resume, read a compact summary of stage, current attempts, HEADs, profile
bindings, dispatch/completion state and evidence paths. Read complete reports or
transcripts only to resolve a named uncertainty. Keep full logs on disk; routine
updates use bounded output deltas and the last meaningful result. Prefer native
completion waits after the saved baseline while independent work progresses.
An empty wait is not completion and does not justify another prompt. Wait
on an attempt with the runtime's `wait`, not a hand-written polling loop:
`settled-no-report` and `background-running` mean inspect the pane, never
mark done.

Send role work only through `prompt`, `followup` or `handoff`. A stuck attempt
moves through `handoff`, a dropped task through `abandon`; a bare
`herdr agent prompt` leaves the run record unable to verify the work. Never send
raw terminal input, such as keys, a typed `/status`, a slash command or shell
text, into a worker pane: raw input is neither role work nor a readiness check.
The one sanctioned pane write is agy's fixed priming prompt below.

The runtime records `created_at`, `dispatched_at`, `acknowledged_at`, `reported_at`
and `verified_at` when those observations occur. Creation is not worker startup;
submission is not acknowledgement, and acknowledgement can mean blocked.
Optional progress views project these facts promptly at each transition. Keep
execution times unknown when historical evidence is missing, with a separate
reconciliation observation time. Never substitute graph collection time for a
worker start/end time or claim an unknown duration is zero. Deliver does not
create or own a Dagr viewer; retained historical graphs remain evidence only.

## Pre-dispatch worktree trust

A fresh worktree checkout has no workspace-trust state in the harness, so its
first interactive start can stop at the harness's own trust dialog. Herdr then
reports `agent start` as `agent_not_ready` (`blocked during startup`), and the
pane consumes anything typed at it. That is the 2026-11-11 retrospective's
uncertain dispatch: a blocked startup, then `/status` and prompt text written
into a live worker pane.

Before dispatch, establish that harness's trust for the exact new checkout and
record the acknowledgement with `worktree-trust`: `task`, `attempt`, the
attempt's planned `harness`, `trusted_path` resolving to the attempt's worktree,
observed `evidence` of the acknowledgement, and one `method`:

- `harness-config`: the harness's own per-directory trust entry was written
  before startup.
- `native-flag`: a verified launch flag accepts the directory.
- `operator-accepted`: the user accepted the dialog in that exact pane.
- `not-required`: a verified harness with no workspace-trust dialog.

Record `harness-config` and `native-flag` before `agent start`. The other two
follow an observation: `operator-accepted` after the user answered the dialog in
that pane, and `not-required` after a verified startup showed no dialog. Record
both before `prompt` or `dispatch-intent`.

Records are append-only and scoped to one checkout and the attempt's planned
harness. `prompt` and `dispatch-intent` refuse an attempt until a matching record
exists, so record the planned profile first and give a profile switch to another
harness its own record. A later attempt in the same checkout reuses its record.

Verified trust stores, checked 2026-11-12: Claude Code 2.1.322 keeps
`projects["<absolute checkout path>"].hasTrustDialogAccepted` in
`~/.claude.json`; Codex 0.167.1 keeps `[projects."<absolute checkout path>"]
trust_level = "trusted"` in `~/.codex/config.toml`. Read the file, add only that
exact path, keep every other entry and value, and write it back atomically so a
concurrent harness start never reads a partial file. Claude's `-p`/non-TTY mode
skips the dialog, but a delivery worker needs the full TUI. Do not clear a trust
stop with `--dangerously-skip-permissions`,
`--dangerously-bypass-approvals-and-sandbox` or another bypass: that broadens
permissions instead of accepting a directory.

agy, Pi, omp and OpenCode have no verified trust mechanism in the current
evidence. Stop for the user at that exact pane, record `operator-accepted` with
the observed post-acceptance state, then dispatch. `herdr worktree create
--trust-repository` is separate: it grants per-request Git trust after the user
verified the repository and never accepts a harness dialog.

Neither a trust dialog nor a startup block is readiness. Never send raw terminal
input, such as keys, a typed `/status`, a slash command or shell text, into a
live worker pane; read it with `agent get`, `agent read PANE --source visible`
and `agent explain --json`. The only sanctioned pane write is agy's fixed
priming prompt in the startup sequence below.

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
   that the pane contains an available interactive shell. Establish trust for
   the exact checkout and planned harness as the section above requires: record
   it with `worktree-trust` before `agent start` when the harness has a config
   or flag mechanism, or from the observed acceptance at its first start. Then
   start `herdr agent start NAME --kind KIND --pane PANE --timeout 30000 -- ARGV...`.
   Names are unique and at most 32 characters. Save actual harness session ID
   after readiness. agy reports its session only when it receives a prompt, so
   for `--kind agy` first record a `checkpoint` naming the pane and the fixed
   priming prompt `Reply with OK only. Do not run tools or touch files.`, send
   it once with `herdr agent prompt PANE TEXT --wait`, then read the bound
   session from `agent get PANE` and pass it as `prompt`'s `worker_session`
   (the attempt's `session` is the Herdr session). Priming grants no work; the
   task prompt still goes through `prompt`. If Herdr omits the session ID for
   any other harness, read the identity from the visible pane and foreground
   process (`agent get`, `agent read PANE --source visible`, `agent explain
   --json`) and bind the displayed session, effective settings and foreground
   process in a checkpoint. Never type
   `/status` or another command into the pane to obtain it: that write is
   indistinguishable from dispatch, and a trust dialog consumes it as
   keystrokes. Use the manual `dispatch-intent` path after those equivalent live
   checks; keep `prompt` strict about its required Herdr session field. A
   missing or ambiguous native identity remains a blocker. Never infer identity
   from a matching cwd or a convenient transcript file. On startup error inspect
   `agent get PANE` and `agent read PANE --source visible`; never blindly start
   again.
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
