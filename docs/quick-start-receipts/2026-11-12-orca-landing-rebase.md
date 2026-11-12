# Orca landing-rebase live check - 2026-11-12

Receipt for the Orca equivalent of the Herdr landing rebase: `orca-rebased`.
The check drove `flyingnobita-deliver-implement` by hand in this Orca session,
landed two tiny tickets that touch different files, and confirmed the second
ticket landed from the orchestrator's rebase plus `orca-rebased`, with no extra
worker round.

Tested source revision: branch `flyingnobita/feat-orca-landing-rebase` at
`b01d5c9` plus the working-tree change that adds `orca-rebased` (committed with
this receipt). Machine: `north-omarchy` (Linux x64).

## Environment

| Component | Version |
| --- | --- |
| Orca | 1.4.256 (`runtimeId c85e6548-7c07-4a9b-ad1b-3c043228d01d`) |
| Codex CLI | `codex-cli 0.167.2` |
| git | 2.56.1 |
| Python | 3.15.2 |

The coordinator was this Orca structured chat session on the OpenCode harness.
Its session ID was `opencode2_6c42761c_221d_47ec_8b01_2e8c76f56e8c`; the runtime
run bound to it used the Orca runtime ID as `host.session` and that chat session
as `host.pane`.

## Isolation

A private disposable Git repository was created at
`/tmp/opencode/orca-rebase-live/repo` with one empty base commit on `main`
(`7bf9d54`). It has no remote and was registered in Orca only for this check.

Two tickets were agreed before dispatch:

| Ticket | Change | Worker worktree | Worker branch |
| --- | --- | --- | --- |
| T1 | add `alpha.txt` containing exactly `alpha` | `orca-rebase-t1` | `orca-rebase/t1` |
| T2 | add `beta.txt` containing exactly `beta` | `orca-rebase-t2` | `orca-rebase/t2` |

Both worktrees were created from `main` at the same base `7bf9d54`, so T2 had
to be rebased once T1 moved `main`.

The delivery runtime record was
`6ab99cbb1f7748d78292f6b7bf1a2c5b` (purpose `implement`, Orca contract 2,
concurrency 2), approved with both tickets as evidence.

## Dispatch

Both workers were pre-created worktrees and launched in parallel:

| Ticket | Native Task | Dispatch | Start receipt |
| --- | --- | --- | --- |
| T1 | `task_fd4ca02c08b5` | `ctx_60220b6e3e8c` | `codex/gpt-6.1-sol`, effort `low`, state `ready` |
| T2 | `task_0bbe6e2d5895` | `ctx_27abdb24a92b` | `codex/gpt-6.1-sol`, effort `low`, state `ready` |

Orca run: `run_5409dafc39ff`.

Each worker received one Task spec containing its packet, the exact file and
content, the check command, the commit command and the report path inside the
private runtime directory. Each sent exactly one `worker_done`; no follow-up
message, retry or replacement Task was created.

| Ticket | `worker_done` | Report commit | Report artifact |
| --- | --- | --- | --- |
| T1 | `msg_42852f9cbe12` | `f308324f3511e8f0db9ac4b77eab7403c4fc1389` | `t1-report.md` |
| T2 | `msg_030a8104b85c` | `0f85b30574fb807f1f613fd668211ee60a98b738` | `t2-report.md` |

## Landing

T1 needed no rebase. The orchestrator ran the planned check at the reported
commit (`sh -c 'test "$(cat alpha.txt)" = alpha'`, exit 0), recorded
`orca-verify`, and fast-forwarded `main` to `f308324`.

T2's report was recorded at `0f85b30` while `main` was still at `7bf9d54`.
After T1 landed, the orchestrator rebased T2's clean worktree onto the moved
target `f308324`.

The gate before the rebase record correctly refused the rebased tip:

```text
$ deliver-runtime orca-verify (job t2, commit ce565f0)
Error: independent verification/commit mismatch
```

The orchestrator then recorded the rebase:

```json
{
  "job": "t2",
  "onto": "f308324f3511e8f0db9ac4b77eab7403c4fc1389",
  "commit": "ce565f03c864ec0f157a9c7d97262ad43b4799a7",
  "evidence": "orchestrator git rebase onto main after T1 landed"
}
```

`orca-rebased` accepted it only because the patch-ids of
`f308324..ce565f0` equal those of the job base `7bf9d54..0f85b30`.

The runtime job then held both values:

```json
{
  "base": "7bf9d5403aaad50389e00fd4a266d20319de9dfe",
  "report": {"commit": "0f85b30574fb807f1f613fd668211ee60a98b738", "outcome": "succeeded"},
  "rebased": {
    "onto": "f308324f3511e8f0db9ac4b77eab7403c4fc1389",
    "commit": "ce565f03c864ec0f157a9c7d97262ad43b4799a7"
  },
  "verified": true
}
```

The orchestrator reran T2's planned check at the rebased tip, recorded
`orca-verify` with `commit ce565f0`, and fast-forwarded `main` to it.

| Ticket | Reported | Landed | Worker rounds |
| --- | --- | --- | --- |
| T1 | `f308324` | `f308324` | 1 |
| T2 | `0f85b30` | `ce565f0` | 1 |

Final `main`:

```text
ce565f0 T2: add beta.txt
f308324 T1: add alpha.txt
7bf9d54 base
```

Two linear commits and no merge commit, so the range is acceptable to a
fast-forward-only publish.

## What this proves

1. A clean Orca worker report can be verified when the orchestrator has not
   rebased it.
2. After the orchestrator rebases a reported Orca job, `orca-rebased` records
   the moved tip only when the patch-ids still match.
3. `orca-verify` then accepts the rebased tip in Orca contract 2, and the
   target fast-forwards to it.
4. T2 landed without a second worker dispatch: both tickets have exactly one
   `worker_done`, one Task and one Dispatch.

## Known limits and deviations

- The run exercised contract 2 only. The JSON-CLI test
  `test_orca_orchestrator_rebase_keeps_the_reported_patches_verifiable` covers
  both contract 1 and contract 2.
- The coordinator was the OpenCode harness, consistent with the limit recorded
  in `2026-11-11-orca.md`; `deliver-orca-preflight` was not used to classify
  this caller.
- The disposable repo had no test suite or changelog beyond the ticket checks;
  the baseline was the single base commit and each ticket's own check.
- Worker prompts were direct ticket instructions rather than the full
  `implement` skill, because the disposable repository has no project skills.
  The landing, evidence and verification path is the one `deliver-implement`
  names.

## Cleanup and retention

Removed after the check:

- Both worker terminals were released, and the `orca-rebase-t1` and
  `orca-rebase-t2` worktrees were removed through Orca.
- The merged branches `orca-rebase/t1` and `orca-rebase/t2` were deleted.
- The disposable repository and its `/tmp/opencode/orca-rebase-live` working
  area were removed; the Orca repository registration for that path remains.

Retained as evidence:

- Orca run `run_5409dafc39ff`, Tasks `task_fd4ca02c08b5` and
  `task_0bbe6e2d5895`, and Dispatches `ctx_60220b6e3e8c` and
  `ctx_27abdb24a92b`.
- The delivery runtime record copied to
  `~/.local/state/flyingnobita-deliver/6ab99cbb1f7748d78292f6b7bf1a2c5b/`,
  including `run.json`, both worker reports, and both captured check outputs.

No credentials or tokens appear in this receipt.
