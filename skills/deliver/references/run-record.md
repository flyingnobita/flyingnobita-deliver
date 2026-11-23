# Run purpose and authorization

The runtime's `create` command takes `repo`, resolved `base`, intended `branch`,
verified `host:{host,session,pane}`, effective `profiles`, optional positive
integer `concurrency` (default 3), and `purpose` (default `delivery`). An optional
`state_root` must be private and outside the project. It creates no workspace.
Old schema-1 records without a purpose retain delivery semantics.

Use `approve` with `run_id`, `approved` and actual user-request/approval
`evidence`. The record has one immutable purpose:

| Purpose | Required approved fields | Allowed roles |
|---|---|---|
| `delivery` | `brief`, `plan`, `seams` | planner before approval; implementer/reviewer/qa after approval |
| `setup` | `setup`: selected profiles and no-edit smoke-test scope | smoke only |
| `review-only` | `review`: target SHA, fixed point, spec and read-only request | reviewer only |
| `review-repair` | `review`: target SHA, fixed point, spec and allowed repairs; `seams`: confirmed repair test interfaces | reviewer and implementer |
| `implement` | `tickets`: the requested ticket references | implementer only |

These fields hold the concrete scope or artifact pointers, not fabricated
booleans. Record setup, review and implement authorization from the user's request and settled
choices. They do not require approval of the original delivery, and cannot be
used to dispatch a full delivery or ship. A change from review-only to repair
needs a new purpose-specific run and the user's repair request.

The orchestrator alone mutates runtime records. Save the approval message or
request reference in evidence. Worker profiles, their success reports and
elapsed time grant no approval. A setup smoke role uses the chosen profile
but its task permits only a no-edit identity/completion report.

For Herdr use the existing `task`/`attempt` interface with the purpose's allowed
role (`smoke` for every setup profile). For Orca use `orca-intent` with that role
and native identities. Paseo uses its native workspace/agent IDs and retains
equivalent request/approval artifacts; it does not need Herdr's prompt API.

`operation-intent` supports worktree-create, agent-start, worktree-remove,
workspace-close, run-create, task-create, worker-release and
opencode-session-create. Each needs a unique `operation_id` and exact `target` object. A successful write is required
before mutation; `operation-result` records its observed result. Other native
mutations use the selected adapter's durable request identity and saved evidence.
`show` inspects state, and `checkpoint` records revalidated stage/caller evidence.
None of these commands performs or authorizes a native host action itself.

New Orca records default to contract 2: see [the Orca contract](orca-contract.md)
for compiled task packets, artifact checks and explicit independent verification.
`orca-settle` never verifies; native success plus clean HEAD is not a stage gate.
Existing contract-1 records remain recoverable without rewriting their history.

## Stage gates

The runtime refuses a stage transition instead of trusting discipline. New runs
record `gate_contract: 2`; a record written by an older runtime keeps its
contract-1 gates, so it resumes without retroactive acceptance work. An Orca
record explicitly created with `orca_contract: 1` also keeps those gates: that
contract carries no typed packet and cannot seal an acceptance, and it exists
only to recover an existing run.

A task's `purpose` types what its verification proves: `preparation`,
`findings`, `implementation` or `acceptance` (default `implementation`).
`verify` seals that purpose, the commit, its tree and the checks it saw. Only an
`acceptance` seal carried by the `reviewer`, or by `qa` when QA was selected,
can gate shipping; an implementer's acceptance, a QA seal for the review gate, a
preparation seal and a findings-only review are all refused. An acceptance seal
also carries its own successful independent checks, as a list of
`{command, exit_code: 0, commit}` for that commit, sealed from a clean checkout
so the reviewed commit is the committed one.

`checkpoint`, `followup` and `verify` refuse while an attempt carries a
settlement older than the run's `settled_bound_s` (1-86400 seconds, default 300,
fixed at `create`): a registered report older than the bound, or a report file
the run never registered. The refusal names each task, attempt, state and age.
Reconciling an uncertain attempt and draining an aged report are never refused,
so when several reports are stale you can process one directly without
acknowledging the others. The only override is an `acknowledgement` reason,
recorded in the run evidence: use it when the settlement waits on a real human
stop, such as an answer only the user can give. A worker still running, a long QA
run and a CI job recorded as a continuation are not settlements, so they are
never refused. An attempt with no reliable timestamp stays resumable rather than
guessed at.

A `ship` or `complete` checkpoint also refuses when:

- a task is neither verified nor abandoned by a user decision nor superseded to
  a verified later task. `supersede` takes `replacement` and
  `coverage:{task, evidence}` naming the task it covers, records the link on both
  tasks, refuses an earlier task, refuses a task with a running attempt, accepts
  an uncertain one only through that coverage, and leaves the old task
  unresolved while its replacement is unverified or abandoned. A free-text
  exception closes nothing, the old task takes no further report or verify, and
  its dependents stay blocked as they do after `abandon`;
- an Orca job is unreconciled, dispatched, or reported without independent
  verification. A recorded, observed rejection closes its job;
- an `operation-intent` has neither an observed `operation-result` nor an
  `operation-disposition`. A disposition needs `evidence` and names a cleanup
  intent (`worktree-remove`, `workspace-close`, `worker-release`) as `retained`
  or `unavailable`; it cannot close any other uncertain native mutation;
- a delivery run has no accepted `reviewer` seal whose tree equals the run's
  integration tree. A merge or squash with the same tree is accepted even though
  the commits differ. The tree is the tip of the run branch, or the
  `approved.landing_ref` recorded after a merge removed that branch; there is no
  checkout-`HEAD` fallback. A run that began before this gate ships by verifying
  an acceptance task now, because an older verified task cannot be resealed;
- `approved.qa` names a QA target and no accepted final-tree `qa` seal exists;
- the checkpoint is `complete` and a continuation is still pending.

## Continuations

A pending worker or hosted gate is not a user stop and not a reason to end a
turn silently. `continuation-open` records `continuation_id`, `kind` (`worker` or
`hosted`), `owner`, `next_observation` and `expected_event`. A `worker` token also
names its `task` and that task's `attempt`; a `hosted` token names its `gate`.
Open one at every wait the pipeline makes on a worker or a hosted check, and
acknowledge it with the observed settlement `evidence` as either
`acknowledgement: native-wake-up` when the harness delivered the event itself,
`acknowledgement: observed-settlement` when you observed the settlement by hand
without any wake-up, or `acknowledgement: continuation-handoff` with
`handoff:{owner,next_observation}` and the `limitation` it replaces. Both closing
claims need `observed: true`; a worker token also stays pending until its bound
attempt is actually `reported` or otherwise processed, and a hosted token keeps
the gate receipt you observed.

A handoff moves responsibility; it proves no settlement, so the token stays
pending and `complete` still refuses it. Only an observed settlement
acknowledgement closes a token. The runtime has no native wake-up channel: no
adapter delivers a settlement into a caller's turn end, so record a native
wake-up only from live evidence of one and otherwise hand off. A refusal cannot
stop an external harness from terminating the turn; the persisted token is the
supported fallback.
