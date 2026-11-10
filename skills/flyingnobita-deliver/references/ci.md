# CI and local checks

During setup, read the project's existing lint/test/build commands, CI workflows
and active local hooks. Check whether the workflow actually runs those commands;
the existence of a workflow or a task named `ci` alone is not coverage.

If checks or automatic execution are missing, record the gap in the brief and
settle it at grilling, unless this session already authorized the choice:

- Checks exist: wire them into the existing provider, or propose a compatible CI
  provider. GitHub-hosted repositories may use GitHub Actions; other repositories
  do not inherit that assumption.
- Checks are missing: establish useful checks first, then automate them.
- CI is unavailable or unwanted: offer active pre-commit/pre-push hooks plus
  recorded local verification before publication, or an explicit deferral.
  Explain that local hooks depend on the machine and can be bypassed.

Record the chosen provider or fallback and commands in the approved plan.
Upstream workflow changes require approved scope; a missing workflow grants no
authority to change repository settings. Existing user authorization settles a
choice without another confirmation.

For approved CI, pin tool/action versions, grant minimal permissions, keep secrets
out of untrusted pull-request checks and avoid duplicate branch/PR runs. Reuse
the existing commands instead of creating a second test definition. Validate
workflow syntax and the commands locally; report remote execution as unverified
until the pushed workflow actually runs. Branch-protection changes are separate.

Done when automatic checks are active and evidenced, or their local fallback or
deferred status is explicit. A passing local command is not a remote CI result.
