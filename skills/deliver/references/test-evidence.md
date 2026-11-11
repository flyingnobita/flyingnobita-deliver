# Test evidence contract

Read this when preparing an implementer report or independently verifying its
tests through the native `report` and `verify` commands. New runs record
`test_contract: 1`. Historical runs without that field keep their original
contract; supplying the new fields opts that report into validation.

## Implementer report

Every implementer report in a new run supplies `test_scope` and `test_evidence`.
For new or changed tests, use `test_scope: "changed"` with one or more groups:

```json
{
  "test_scope": "changed",
  "test_evidence": [
    {
      "id": "greeting",
      "kind": "behavioral",
      "subject_commit": "<full commit before the behavior was fixed>",
      "test_commit": "<full commit containing the exact test snapshot>",
      "tests": [
        {"path": "tests/test_greeting.py", "sha256": "<SHA-256 of test file bytes>"}
      ]
    }
  ]
}
```

These fields extend the normal report identity, final `commit`, `checks`,
`questions` and `observed_profile`; they do not replace them. Replace
angle-bracket values with actual hashes. Commit hashes must be full Git object
IDs. Paths are checkout-relative files. The runtime reads each cited Git blob
and checks its content hash. It rejects a behavioral red whose subject is the
final reported green commit.

Behavioral red evidence is per test, as the build brief requires
([pipeline.md](pipeline.md)). A group is behavioral only if its own test fails
on its `subject_commit`. A whole-file failure, a failure produced by another
test in the same file, and a failure against an intermediate commit are all
rejected, not accepted as that group's red.

Every conventionally named changed test must appear in a group. Detection covers
`test/`, `tests/`, `__tests__/`, `spec/`, `specs/`, `test_*`, `*_test.*`,
`*.test.*`, `*.spec.*` and `*.bats`. The orchestrator also checks custom seam
paths against the approved plan; naming conventions cannot discover every test.

Exceptions remain explicit:

- `kind: "guard"`: give a plan-backed `reason`; the test must pass before and
  after the change.
- `kind: "bootstrap"`: give a plan-backed `reason`; the before receipt must
  identify deliberate product/package absence, rather than a broken fixture.
- No new or changed tests: use `test_scope: "none"`, `test_evidence: []` and a
  nonempty `test_reason`. Review that exemption independently.
- Documentation only: use `test_scope: "docs-only"`, the empty list and a
  nonempty `test_reason`. The runtime requires documentation file extensions.

Conventional changed test files cannot use either no-test exemption. Deleted
tests are not new/changed tests, but their removal still needs review.

## Independent verification receipts

The orchestrator runs the tests independently and saves JSON receipts outside
the worker checkout, normally in the private run directory. Each receipt has:

```json
{
  "run_id": "<run ID>",
  "task": "<task ID>",
  "attempt": "<attempt ID>",
  "phase": "before",
  "subject_commit": "<subject commit for this phase>",
  "test_commit": "<the group's test snapshot commit>",
  "tests": [
    {"path": "tests/test_greeting.py", "sha256": "<same file hash as the group>"}
  ],
  "command": ["pytest", "tests/test_greeting.py"],
  "returncode": 1,
  "classification": "assertion-failure"
}
```

The before subject equals the group's `subject_commit`. The after subject equals
the report's final `commit`. Both phases use the group's exact test snapshot and
path/hash list. Each `command` array targets only the group's named test, in the
filtered form the build brief names; a command that runs the whole file or
several tests does not establish that group's red. Keep commands free of
credentials and retain logs separately.

Pass their absolute paths and content hashes to `verify`:

```json
{
  "test_results": [
    {
      "id": "greeting",
      "before": {"path": "/private/run/before.json", "sha256": "<receipt hash>"},
      "after": {"path": "/private/run/after.json", "sha256": "<receipt hash>"}
    }
  ]
}
```

Include the normal verification identity, host, final commit and independent
`evidence`. One result pair is required per group. Receipts must be regular
files, not symlinks. Their identities, commits, test lists and hashes must match.

| Kind | Before classification / status | After classification / status |
| --- | --- | --- |
| behavioral | `assertion-failure` / positive nonzero exit | `passed` / 0 |
| guard | `passed` / 0 | `passed` / 0 |
| bootstrap | `bootstrap-absence` / positive nonzero exit | `passed` / 0 |

Fixture errors, missing tools and killed processes do not establish behavioral
reds. The runtime checks the declared failure class and bindings; it does not
interpret logs or execute arbitrary receipt commands. The orchestrator must
inspect the failure and attest that it proves the intended behavior. Accepted
receipt contents and hashes are retained in the run's verification evidence.
