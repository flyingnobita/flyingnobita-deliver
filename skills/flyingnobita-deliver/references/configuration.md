# Delivery configuration

Read at setup and resume. Project configuration is optional:
`docs/agents/delivery.toml`. Resolve each setting as explicit run override,
project value, then adapter default. Record the effective settings in the brief
and run. Configuration never grants publishing, merging or permission authority.

```toml
[delivery]
max_workers = 3
human_schedule = "normal" # normal | front-load | back-load
landing = "standard"      # standard | leave | pr
commit_skill = ""         # optional custom commit skill (defaults to repository commit rules)

[hosts.orca]
worktree_setup = "run"    # run | skip | inherit

[hosts.orca.roles.planner]
harness = "codex"
# model and effort optional: inherit Orca's configured defaults when omitted

[hosts.orca.roles.implementer]
harness = "codex"

[hosts.orca.roles.reviewer]
harness = "claude"

[hosts.orca.roles.qa]
harness = "codex"
```

The example shows the file's shape; its harnesses are not defaults. Orca's
installed defaults are in [orca-profiles.toml](orca-profiles.toml) and Herdr's
in [herdr-profiles.toml](herdr-profiles.toml).

## Keys

- `[delivery]`
  - `max_workers`: positive integer, excluding booleans.
  - `human_schedule`: order of user-only steps, such as adding a CI secret. See
    [scheduling.md](scheduling.md).
    - `normal`: start ready agent work; notify whenever human work is ready.
    - `front-load`: put human work first while independent agent work proceeds.
    - `back-load`: finish independent agent work first, then notify once.
  - `landing`: how the run ends.
    - `standard`: use the existing direct/upstream ship rules and approval
      gates.
    - `leave`: finish verification and report the committed branch; preserve
      its workspace and artifacts. No push, PR or merge.
    - `pr`: prepare/open a PR using the same publication approval rules as
      `standard`, but never merge it. Retain the workspace for review
      follow-ups.
  - `commit_skill`: optional custom commit skill name. When omitted or empty,
    workers follow repository commit rules with safe built-in defaults.

### Host settings

- **Orca:** `[hosts.orca.roles.<role>]` uses `harness`, optional `model` and
  `effort`. Roles are planner, implementer, reviewer and qa. No orchestrator
  replacement. The adapter uses the implementer for repairs.
  Runtime-owned launch permissions are inspected, never silently changed.
  `[hosts.orca]` `worktree_setup` is `run`, `skip` or `inherit`, passed as
  `--setup` to `worktree create`.
- **Herdr:** preserve existing `[planner]`, `[implementer]`, `[reviewer]`,
  `[qa]` project tables. Pass only those role tables to `profiles`; `[delivery]`
  and `[hosts]` are not role names. Harnesses are `claude`, `codex`, `agy`, `pi`,
  `omp` and `opencode`; the adapter holds each one's supported roles, mode values
  and verified flags. Herdr's defaults and native validation remain in its
  adapter. Pass resolved `max_workers` as `concurrency` to `create`.
- **Paseo:** existing live profile IDs remain authoritative. `[delivery]`
  controls scheduling and landing; do not rewrite live profiles or reinterpret
  Orca/Herdr settings as Paseo permissions.

## Validation

- A shared policy value must have the type and enum above.
- An `effort` requires a supported explicit `model`.
- Report unknown settings before launch, never drop them silently. Preserve
  them when editing an existing file.
- Validate launches and keep requested and effective values.

## Base branch

The default base is the remote default branch. A different base needs explicit
run approval and is recorded with its resolved SHA; legacy `base_branch` is not
automatically a new delivery's base or merge target.

## Resume

At resume use the saved concurrency and policy, reconciling any requested
change before dispatch. Do not silently change an in-flight run from edited
project defaults. When a legacy `orchestration.toml` exists, read
[migration.md](migration.md) before launching new work.
