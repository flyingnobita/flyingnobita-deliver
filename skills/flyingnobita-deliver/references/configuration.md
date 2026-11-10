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
in [herdr-profiles.toml](herdr-profiles.toml). Validate launches and keep
requested and effective values.
An `effort` requires a supported explicit `model`. Unknown settings must be
reported before launch, not silently dropped. Preserve them when editing an
existing file. A shared policy value must have the type/enum above;
`max_workers` is a positive integer, excluding booleans.

- **standard:** use the existing direct/upstream ship rules and approval gates.
- **leave:** finish verification and report the committed branch; preserve its
  workspace and artifacts. No push, PR or merge.
- **pr:** prepare/open a PR using the same publication approval rules as
  standard, but never merge it. Retain the workspace for review follow-ups.
- **commit_skill:** optional custom commit skill name. When omitted or empty, workers
  follow repository commit rules with safe built-in defaults.

The default base is the remote default branch. A different base needs explicit
run approval and is recorded with its resolved SHA; legacy `base_branch` is not
automatically a new delivery's base or merge target.

## Host settings

- **Orca:** `[hosts.orca.roles.<role>]` uses `harness`, optional `model` and
  `effort`. Roles are planner, implementer, reviewer and qa. No orchestrator
  replacement. The adapter uses the implementer for repairs.
  Runtime-owned launch permissions are inspected, never silently changed.
- **Herdr:** preserve existing `[planner]`, `[implementer]`, `[reviewer]`,
  `[qa]` project tables. Pass only those role tables to `profiles`; `[delivery]`
  and `[hosts]` are not role names. Harnesses are `claude`, `codex`, `agy`, `pi`,
  `omp` and `opencode`; the adapter holds each one's supported roles, mode values
  and verified flags. Herdr's defaults and native validation remain in its
  adapter. Pass resolved `max_workers` as `concurrency` to `create`.
- **Paseo:** existing live profile IDs remain authoritative. `[delivery]`
  controls scheduling and landing; do not rewrite live profiles or reinterpret
  Orca/Herdr settings as Paseo permissions.

At resume use the saved concurrency and policy, reconciling any requested
change before dispatch. Do not silently change an in-flight run from edited
project defaults. When a legacy `orchestration.toml` exists, read
[migration.md](migration.md) before launching new work.
