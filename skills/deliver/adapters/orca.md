# Orca adapter

Use after [host detection](../references/host-detection.md). Resolve the Orca CLI
for the session: `ORCA_CLI_COMMAND` if set; `orca-dev` in a dev checkout exposing
`ORCA_DEV_REPO_ROOT`; `orca-ide` on Linux outside an Orca-managed terminal (never
bare `orca` there to prevent starting the GNOME screen reader); otherwise `orca`.
Load the full version-matched guide directly with `ORCA skills get orchestration --full`
(fetching any omitted references with `ORCA skills get orchestration --reference references/<file>.md`
if output is truncated), or through `orca-orchestration` when installed. A missing
local discovery wrapper does not block if the native guide is available. Use the
resolved CLI for this entire run. This adapter targets local Git worktrees; remote execution
requires a separately validated execution-host and evidence path. The initiating
session stays the coordinator, with its existing model and settings.

Read [the Orca contract](../references/orca-contract.md) before caller preflight,
task creation, settlement or verification. New runs use its validated task
packets, durable artifacts and separate independent gates.

## Preflight and profiles

Read [configuration.md](../references/configuration.md). Resolve the needed
roles from [orca-profiles.toml](../references/orca-profiles.toml), then project
and run `hosts.orca.roles` tables: four roles for delivery, reviewer for
review-only, reviewer/implementer for review-repair,
implementer for implement, and the selected profiles
for setup. A project or run table replaces that role's default whole, so a
changed harness never inherits another harness's model. If a default is
unavailable, use `deliver-setup` (or `flyingnobita-deliver-setup`) to choose
among installed agents
at the grilling stop. Omit unset model and effort flags; never silently
substitute a model.
Inspect launch permissions in Orca's actual settings/receipt. `worker-start`
does not expose a per-role permission-mode flag in the inspected 1.4.237 CLI.
Do not invent one or rewrite global settings to obtain a launch.

Planner/reviewer briefs prohibit project edits. Record whether this is enforced
by the effective host permissions or only by the role contract; do not label a
bypass launch sandboxed. If the requested profile requires enforced read-only
execution that the host cannot supply, report that mismatch before launch.
Native trust/tool dialogs go to the user in the exact worker surface. Never
answer a dialog by sending terminal keystrokes or broadening permissions.

Validate agent/model/effort with setup's no-edit smoke task and inspect
`launch.requested` versus `launch.effective` on every real start. The native
review skill may need its own nested agents: check that capability separately.
The reviewer does not dispatch repairs, so Deliver adds no nested worker level.

## Durable delivery record

Use `deliver-runtime create` with canonical repo, resolved base, unique intended
work branch, effective profiles and `concurrency`. Host binding is
`{host:"orca",session:<runtimeId>,pane:<verified caller handle/session>}`.
Keep the runtime ID stable on resume; record verified replacement caller
evidence with `checkpoint`. A runtime change requires explicit reconciliation
in a new run, not silently rewriting the old binding.

For setup or standalone review, use the purpose and approval fields in
[run-record.md](../references/run-record.md). `setup` jobs use role `smoke`
with the selected profile and a no-edit contract; they never gain build approval.

State defaults to `~/.local/state/flyingnobita-deliver/<run_id>/run.json`.
Save brief, plan, approvals and reports beside it, outside project commits.
For a delivery, use `approve` only after actual brief/plan/seam approval. `checkpoint` records
stage/evidence; `show` recovers it. The helper records evidence supplied by the
coordinator; it neither validates native authority nor runs tests for you.

For resource mutations use `operation-intent` before the native command and
`operation-result` after its observed receipt. Gate the mutation on a successful
intent write. Record exact target, native request ID and argv where applicable;
redact credentials. A lost result is an uncertain operation to reconcile, never
permission for another fresh request. Orca's native `--retry-request` and
`request-show` own replay/recovery; use their current guide and receipts.

## Operations

In these examples `ORCA` means the already resolved executable. Use structured
arguments or properly quoted argv; do not interpolate task text as shell code.

| Operation | Native operation and delivery rule |
|---|---|
| Bind run | `orchestration run-create --objective "deliver <work>" --json`; save returned Run ID. Resume with `run-use --id <id>` only after verifying coordinator ownership. Never take over an active coordinator. |
| Create workspace | `worktree create --repo path:<repo> --name <unique> --branch <branch> --base-branch <resolved-base> --setup <policy> --json`. Without `--branch`, Orca names the branch `<git-user>/<name>` and suffixes a taken name (Orca 1.4.258, 2026-11-14). Keep UI focus. Record returned full worktree ID, path and actual branch. The creation receipt is authoritative, not the intended branch label in the draft record. |
| Create task | `orchestration task-create --spec <brief> --json`. Journal this mutation and save its Task ID before dispatch. Use explicit dependencies when useful, but dispatch only after delivery blockers are verified and merged. |
| Start role | `orchestration worker-start --task <id> --worktree id:<full-worktree-id> --agent <harness> [--model <id> --effort <level>] --json`. Pre-created worktrees give an exact base before dispatch. Do not pass creation flags for an existing worktree. Omit `--retry-request` for a new start: Orca accepts only the native request UUID it reported for the original request, and only when replaying that request. |
| Running follow-up | `orchestration send --to dispatch:<id> --subject <subject> --body <guidance> --json`; enqueue is not proof it was read. |
| Settled follow-up | Create a new native Task and delivery job. Reuse a proven agent with `worker-start --task <new-id> --terminal <handle> --worktree id:<full-id> --json`; omit model/effort on reuse. Otherwise start fresh with saved context. |
| Wait | `orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 60000 --json`. Process every row before acknowledging the delivery. |
| Answer question | `orchestration reply --id <message-id> --body <answer> --json`, only when the approved plan or a user decision supplies the answer. Resume pending asks by message ID after timeout. |
| Settle resource | After accepted completion, immediately reuse, explicitly user-requested retain, or `worker-release --dispatch <id>`. Native settlement is separate from the delivery gate. Preserve the worktree for verification even when the worker is released. |
| Notify | Report the exact task/worker and needed decision in this conversation. Use an available native notification or guarded `notify-send`/macOS notification; no private-message service is implied. |
| Remove workspace | After verified landing, fresh ownership and clean-tree checks, journal and call `worktree rm --worktree id:<full-id> --json`, without force. It removes the checkout and its registration but keeps the branch: delete it with `git branch -d`. Preserve user-owned, reused or ambiguous workspaces. |

Each Task brief names target, change, constraints, ownership and observable
acceptance; points to the approved artifacts and relevant role instructions;
and requires the native preamble's exact lifecycle commands. Workers read
follow-ups at natural checkpoints, send one `worker_done` with actual IDs,
outcome, checks and report path, then idle. Implementers follow
repository commit rules (or a configured custom commit skill); no worker pushes,
deploys or uses old `orch-*`
templates. Save planner output through `worker-read` when the profile cannot
write a plan artifact; inspect and persist it before the plan stop.

## Native evidence commands

All commands take JSON on stdin and include delivery `run_id` and optional
`state_root`. These journal native attempts; they never dispatch or retry.

1. Before `worker-start`, call `orca-intent` with unique `job`, `request_id`,
   `native_run`, `native_task`, `role`, `worktree`, `branch`, compiled `packet` and current `base`
   SHA. This checks approval, isolation, concurrency and duplicate intent.
   The base must be the coordinator-verified integration tip for that ticket.
   `request_id` identifies the delivery record; it is not Orca's native request
   UUID and never goes to `--retry-request`.
2. After the launch, call `orca-receipt` with `job`, matching native run/task/
   request, actual `dispatch` and `evidence` from the receipt. A failed start
   may still own resources; inspect its native receipt instead of assuming no
   dispatch exists. Preserve an unresolved intent until the outcome is known.
3. After accepting native settlement, call `orca-settle` (or `orca-report`) with `job`, matching
   native run/task/dispatch, `outcome`, actual worktree `commit`, nonempty
   `checks`, `questions` list, `artifact_path` and settlement `evidence`. Reports are immutable.
   A proven failed startup can be normalized as a failed report with its native
   failure evidence; a timeout or missing receipt cannot. Retain detailed role
   artifacts beside the immutable JSON report before removing any workspace.
4. After the orchestrator rebases a reported branch onto the moved target, call
   `orca-rebased` with `job`, `onto`, the actual clean worktree `commit` and
   `evidence`. The runtime accepts only an `onto` descending from the job base
   whose `onto..commit` patch-ids equal the report's `base..commit`; a conflict
   or changed patch goes back to the worker. Record it before verifying the
   rebased tip.
5. After independently running the stage's checks, call `orca-verify` with
   `job`, matching `dispatch`, exact `commit` (the rebased tip when step 4
   recorded one), revalidated runtime ID as `host`
   and command/result `evidence` plus the contract's structured `verification`. A failed report, pending question, dirty tree
   or changed HEAD cannot pass. Gate status is distinct from native success.

If native rejection occurred before any Dispatch existed, use `orca-rejected`
instead of inventing a completion report: supply `job`, matching native run/task/
request, `request_state:"completed"`, inspected `task_state` (`ready` or `failed`),
`dispatch_absent:true`, and native rejection/resource-inspection `evidence`.
Orca 1.4.237 can refuse a dependency-blocked Task before recording a request.
For that case only, pass `request_state:"absent"`, `task_state:"pending"` and
`preflight_rejection` containing the original complete JSON error response.
It must be `task_not_startable` with the same Task ID, request ID and pending
status. Preserve the immediate task snapshot and fresh no-Dispatch/resource
inspection in `evidence`. An absent receipt without this direct matching refusal
remains unresolved. Record the negative probe's expected failure in native Task
state after inspection; a real blocked task instead remains pending.

The helper requires the original clean base. It retains the failed intent and
frees its slot; it does not authorize a retry. Other missing or pending requests,
unsettled resources or changed work remain unresolved. Follow the native
recovery receipt before another attempt, and use a new job/request only after
the old outcome is proven.

New review/fix iterations use new jobs and native Tasks, preserving history.
An infrastructure retry uses the original native Task and explicit `--retry-of`
only after the guide permits it; record a new job/request and its relation to
the old failed dispatch. Do not use Herdr's `attempt`, `prompt` or `recover`
commands for Orca. Its native circuit breaker remains authoritative.

## Resume and cleanup

Read the delivery record and native run/tasks/workers. Follow pagination and
scope `worker-list --run <id>`; read native reports by Dispatch ID, including
archived output. Compare saved requests, commits and worktree ownership before
any mutation. `request-show` resolves lost receipts using the original request
identity. Never create a second editor because a wait was empty or a tab is gone.

After three empty waits inspect native `projection.nextAction`. `unverifiable`
does not authorize stop, abandon, retry or release. A worker's explicit failed
report goes to scheduling's `needs-info`; it is not an infrastructure retry.
If the installed runtime cannot prove the required state, report the blocker
and preserve it. Do not reset orchestration state.

Before cleanup, ensure native reclaimable workers have an ownership decision,
save all artifacts, verify the branch was landed by ancestry or identical tree
after squash, and recheck status and ownership immediately before removal.
For `leave`, partial runs and upstream PRs, retain integration workspaces.
Keep native and delivery records after cleanup. Final reporting distinguishes
native outcome, independently verified gates and any remaining acceptance gap.
