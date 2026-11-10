# Orca caller, task and verification contract

Read before native work in new Orca runs, including nested review coordination.
The source runtime supplies deterministic checks; Orca owns dispatch, retry,
settlement and cleanup. These checks do not authenticate arbitrary user-supplied
JSON or prove a worker obeyed its instructions.

## Caller preflight

After loading the full version-matched Orca orchestration guide (via
`ORCA skills get orchestration --full` or `orca-orchestration`), run
`deliver-orca-preflight` with `{"repo":"/absolute/repository"}` on stdin from
this executing agent's checkout. It uses only read-only Orca status, own-handle
lookup and `run-current`, Git identity and process ancestry. Output is `orca`
(`absent`, `confirmed`, or `broken`), verified `host` and compact `evidence`.
Feed its classification to `select-host` alongside Herdr/Paseo checks; save its
host/evidence in the run. It never launches Orca, lists possible callers or
injects identity variables.

Terminal and structured-chat paths are distinct. Terminal agents need their own
inherited handle and live pane/harness binding; no chat caller field is required.
Chats require their injected session's live host-resolved caller. Refusal does
not fall back to a sibling terminal. Linux compares named harness ancestry and
inherited pane/session fields; macOS checks named ancestry and live own-pane
binding without dumping parent environments. Multiple harness ancestors, stale
handles, mismatched repository/host/runtime/session and unknown OS stay broken.
A chat `/clear` lineage whose returned canonical ID differs stays unresolved
until the installed host guide supplies a supported resolution.

## New run contract

`create` defaults new Orca records to `orca_contract:2`. Existing records lacking
this field, and explicitly imported `orca_contract:1` records, retain the old
recovery interface. Use contract 1 only to recover an existing run, never to
bypass a failed check on new work. Keep records immutable across upgrades.

Before creating a native Task, compile `deliver-runtime orca-task` with a
`packet` object:

```json
{
  "packet": {
    "target": "Exact workspace, fixed point and files",
    "change": "Concrete result required",
    "constraints": "Read-only review; local-only results",
    "ownership": "Findings artifact only; no edits or repairs",
    "acceptance": "Separate Standards/Spec findings at the named HEAD",
    "profile": {"harness":"antigravity","model":"gemini-3.8-flash-medium","effort":"medium"},
    "report_path": "/private/run-directory/review.md",
    "verification_commands": [["git","diff","--check"]],
    "axis": "spec"
  }
}
```

The profile above is an example, not a default. `axis` is optional for ordinary
roles; use `standards` or `spec` for each nested review axis. Compiler output is
`spec` and its digest. Pass that exact spec to native `task-create`; save the
packet and compiled output. Each axis needs its complete spec before launch.
The compiler checks required structure, not whether prose or chosen commands
are adequate. The coordinator reviews their meaning and approved scope.

Include the same packet in `orca-intent`. Its profile must equal the selected
role profile; its report must live inside this private run directory and outside
all disposable workspaces. Plan meaningful independent commands before dispatch:
behavior tests and lint for build, evidence/diff checks for planning and review,
and actual user-facing commands for QA. No new approval is implied by compiling.

Nested reviewers use the same compiler for their complete axis packets before
native task creation. They return packet/spec evidence, every attempt and the
resulting durable axis reports in their final review artifact. They do not gain
access to the parent delivery record's writer lock or coordinator mutations.

## Settlement and independent verification

After matching native settlement, `orca-settle` is the explicit name for
`orca-report`; both only persist the immutable report and leave `verified:false`.
Supply existing report fields plus `artifact_path` matching the packet. The
helper reads the nonempty owned regular artifact and records its hash before
worker release. No report file means settlement evidence is incomplete; preserve
native ownership and recover the artifact before cleanup. A rejected start uses
`orca-rejected`, not a fabricated report artifact.

Only a separate `orca-verify` call can pass the delivery gate. In contract 2,
include `verification` with:

- `stage` equal to the job's role;
- `checks`, in the planned argv order, each with exact `argv`, integer
  `exit_code:0`, the verified `commit`, and an `output_path` inside this private
  run directory containing the coordinator's captured output (empty successful
  output is valid);
- for reviewers, explicit `verdict:"clean"` and integer `must_fix:0` after reading
  both axes and checking the reviewed HEAD.

Worker output is not independent evidence: check-output paths must differ from
the worker report. The report hash, native identities, runtime, clean worktree
and commit are rechecked. Human reasoning such as red-failure interpretation,
check completeness and review classification remains the coordinator's job.
A successful native review with findings settles normally but cannot pass the
clean-review gate; dispatch repairs through the existing loop.
