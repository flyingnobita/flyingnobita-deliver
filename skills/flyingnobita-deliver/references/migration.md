# Migrate the Orca workflow

Read when `docs/agents/orchestration.toml` exists or a user requests the
retired `orch-*` workflow. New work uses Deliver. Existing runs retain their original contract
until they settle; changing skill names is not a lifecycle takeover.

## Preview configuration

Parse the legacy file with Python `tomllib`, then send
`{"legacy": <parsed object>}` on stdin to `deliver-runtime migrate-orca`.
This pure JSON command writes no configuration and launches nothing. It returns
`config`, the complete `legacy` object, `missing_roles` and `decisions`.

Review the preview with the user in setup or Deliver's grilling stop:

- Preserve implementer/reviewer agent, model and effort where supported.
- Choose planner and QA settings explicitly. Keep the initiating orchestrator;
  record old orchestrator/fixer settings in the migration record only.
- Preserve concurrency and setup policy. Validate all requested settings on
  the installed host before accepting a profile.
- Default migrated landing to `leave`. Explain legacy `pr` and local `merge`
  separately; use the shared landing rules only after a concrete choice.
- Replace question-timeout assumptions with escalation of unresolved decisions.
- Review `base_branch`, sandbox, network and unknown fields individually.
  They are retained in the original file and preview, not silently applied to
  unrelated sessions or automatically translated into broader permissions.

Back up an existing `delivery.toml` before editing, merge approved values and
preserve its unknown keys. Do not overwrite newer delivery settings from an
older orchestration file. Retain the old file and preview as migration evidence.
Repeating setup with unchanged decisions should make no file changes.

## Retired workflow

The four `flyingnobita-orch-*` skill directories and worker templates were
removed from source on 2026-10-24 after bounded native acceptance and both-host
legacy-run disposition. Use `flyingnobita-deliver-setup` for setup,
`flyingnobita-deliver` for implementation, `flyingnobita-deliver-review` for
review/repair and the [workflow guide](workflow.md) for questions.

All new workers follow repository commit rules directly (or an explicitly configured
custom commit skill). A retired template read no longer satisfies the Claude, Codex
or Antigravity commit gate. Local commit authority still grants no publication or
deployment authority.

Source removal and installed-copy removal are separate checks. When cleaning up legacy
installations, remove installed legacy skill directories only after reviewing local
changes and backing up any custom modifications.

Native run records, reports, worktrees and configuration migration evidence
are outside the removal list. A matching live process discovered later
requires fresh native ownership/authority checks; retirement authorizes
no takeover or process termination.

Acceptance scope and limitations: bounded checks do not imply OS reboot, desktop
restoration or unverified profile compatibility beyond checked evidence.
