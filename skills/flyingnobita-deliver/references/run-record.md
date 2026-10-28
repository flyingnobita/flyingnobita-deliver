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

These fields hold the concrete scope or artifact pointers, not fabricated
booleans. Record setup/review authorization from the user's request and settled
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
workspace-close, run-create, task-create and worker-release. Each needs a
unique `operation_id` and exact `target` object. A successful write is required
before mutation; `operation-result` records its observed result. Other native
mutations use the selected adapter's durable request identity and saved evidence.
`show` inspects state, and `checkpoint` records revalidated stage/caller evidence.
None of these commands performs or authorizes a native host action itself.

New Orca records default to contract 2: see [the Orca contract](orca-contract.md)
for compiled task packets, artifact checks and explicit independent verification.
`orca-settle` never verifies; native success plus clean HEAD is not a stage gate.
Existing contract-1 records remain recoverable without rewriting their history.
