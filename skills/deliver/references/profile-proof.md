# Effective profiles and quota replacements

For native task attempts, new runs record `profile_contract: 1`. Their `verify`
command requires immutable per-attempt proof of the effective profile, availability
and harness session. Historical runs without the field remain resumable; no
previous observations or timestamps are fabricated.

`attempt` takes its requested profile from the resolved role defaults. After
native startup inspection, the orchestrator records:

```json
{
  "run_id": "<run ID>",
  "task": "<task ID>",
  "attempt": "<attempt ID>",
  "observed_profile": {
    "harness": "pi",
    "model": "deepseek/deepseek-flash",
    "effort": "high",
    "mode": "default"
  },
  "worker_session": "<actual harness session ID or path>",
  "availability_verified": true,
  "evidence": "<retained native startup/status evidence>"
}
```

Pass this object to `profile-bind` before dispatch when the session is available,
or after the adapter's required priming/identity discovery. Use canonical model
IDs, including provider qualification when required. Proof is the orchestrator's
startup attestation, not a worker's preferred model or a credentialed model call.
The runtime validates profile fields, equality with the authorized request and
binding to any already-recorded worker session. It does not discover a model
from the name of a transcript file.

Every report in a run with `profile_contract: 1` must also carry
`observed_profile` with the same four canonical fields (`harness`, `model`,
`effort`, `mode`). `report` refuses a missing, partial, differently named or
mismatched effective profile, and `verify` rechecks it against the authorized
request. A report that names its mode, effort or model in another vocabulary, such
as native `default` for a requested `full-access` or `not exposed` effort, cannot
register or verify. Historical runs without the contract remain resumable.

Quota changes are supported. When the stopped worker can still write a
partial-work report, retain its exact HEAD, report and observed settings and use
`followup`. When it cannot, for example because the quota refusal arrived before
any report, `reconcile` the live worker and use `handoff`. Either command takes
the new `requested_profile` and a nonempty `profile_authorization` pointing to
the user's choice. The new attempt receives the new request and requires fresh
proof; the old proof stays unchanged. This also applies to a model change inside
the same native session. Resource replacement still follows the adapter's
identity and ownership checks.

A run-level profile table is the historical requested default, not a substitute
for per-attempt observations. An override on initial `attempt` or `profile-bind`
also needs `requested_profile` plus `profile_authorization` when it differs from
the saved request. An unconfigured request must be explicitly authorized before
binding. Rebinding existing proof is refused; record a new attempt instead.
