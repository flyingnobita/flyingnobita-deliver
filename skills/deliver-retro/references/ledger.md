# Retro ledger

The ledger is how one retro learns from the last: which findings recur, which
fixes held, and how each gate and role profile performs over many runs. It
lives beside the run records it cites, private and outside every checkout:
`<state root>/retros/`, using the state root from [evidence](evidence.md). It
covers the runs on this host. Create the directory with mode 0700 on first use.

Write one file per retro, `<YYYYMMDD-HHMM>-<first run ID>.json`, through a
temporary file and rename. Never store secrets, prompts or transcript excerpts;
store pointers and counts.

```json
{
  "schema": 1,
  "created_at": "2026-10-28T09:00:00+08:00",
  "runs": [{"run_id": "...", "repo": "/abs/repo", "host": "herdr", "route": "single"}],
  "reworks": [{"run_id": "...", "kind": "plan-revision", "origin_stage": "plan", "origin_role": "planner", "minutes": 25}],
  "checks": {"C1": "finding", "C2": "clean", "E1": "finding"},
  "gates": {"red_check": {"caught": 0, "minutes": 4}, "review": {"caught": 2, "minutes": 30}, "qa": {"caught": 0, "minutes": 12}, "verify": {"caught": 1, "minutes": 6}},
  "profiles": [{"role": "implementer", "host": "herdr", "harness": "codex", "model": "...", "effort": "medium", "attempts": 3, "reworks_originated": 2, "minutes": 90}],
  "upstream": {"skill": "mattpocock-retro", "revision": "skill-lock:335c1862a43da9d629abafdb79ca0c0de118be08", "updatedAt": "2026-11-11T06:22:50Z", "available": true},
  "candidates": [{"id": "C1-1", "check": "C1", "title": "...", "severity": "rework", "fix_type": "skill-text", "owner_file": "references/pipeline.md", "measure": "...", "recurrence": 0, "status": "proposed", "commit": null}]
}
```

Fill `route` with `single` or `graph`, and `host` with the selected adapter.
`checks` holds one result per coordination and role check (C1 to C7, R1 to R9)
and per environment category (E1 to E7), so a clean category is still recorded.
`upstream` records the compared copy from step 1: its `revision` and the lock's
`updatedAt` date when a copy was installed, or `available` false with no
`revision` when none was.
The `...` values are placeholders; a real entry holds observed values or omits
the field.

Candidate `status` moves `proposed` to `accepted` or `declined` on the user's
choice, then to `implemented` with its `commit`. A later retro sets `held` or
`regressed` after checking the measure on runs that started after the commit.
Edit only the status fields of a past entry; everything else is the record of
what that retro saw.

When the user accepts the final offer to centralize TODOs, also add/update the
selected candidates' `tracker_refs` with verified URLs or local tracker paths
and entry IDs. This is a bookkeeping exception to the status-only rule: preserve
all original findings, measures and evidence. Existing entries without this
optional field remain valid. Logging a proposal does not change its status to
`accepted` or authorize implementation.

A trend needs runs, not retros: count each run once even when several retros
read it.

Keep `minutes` fields numeric. A duration bounded by a transcript and an artifact
write time stays numeric, and its two sources stay in that retro's evidence.
Format user-facing table durations as `Hh Mm` (337 minutes becomes `5h 37m`);
presentation does not change stored evidence.
