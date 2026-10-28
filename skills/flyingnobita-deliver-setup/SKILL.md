---
name: flyingnobita-deliver-setup
description: Check delivery prerequisites and offer fixes, configure delivery profiles and project defaults, validate a delivery host, or migrate legacy Orca orchestration settings to flyingnobita-deliver.
---

# Set up delivery

Configure the requested repo for `flyingnobita-deliver`. This is an idempotent
setup operation, not a delivery run. Existing valid defaults need no repeated
interview. Inside Deliver, join unresolved choices to its grilling stop.

1. Read the repo's rules and the shared
   [configuration](../flyingnobita-deliver/references/configuration.md).
   Detect the host using [host detection](../flyingnobita-deliver/references/host-detection.md).
   Read only its adapter: [Orca](../flyingnobita-deliver/adapters/orca.md),
   [Herdr](../flyingnobita-deliver/adapters/herdr.md), or
   [Paseo](../flyingnobita-deliver/adapters/paseo.md).
2. Run every check in [prerequisites](references/prerequisites.md) for the
   selected host and report its table. For each failed required row, give the
   fix and its link, and apply it only on the user's approval. A blocking row
   (missing `flyingnobita-clean-commit`, helper or host component) stops setup
   before smoke tests. Then present the optional section separately.
3. If legacy configuration or an old run exists, read
   [migration](../flyingnobita-deliver/references/migration.md). Preview changes
   and inventory existing runs before proposing removal. Do not commandeer them.
4. Resolve planner, implementer, reviewer and QA settings. Recommend a distinct
   reviewer model/harness when available. Ask only for missing/unsupported
   choices and changes in authority. Keep the initiating orchestrator unchanged.
   Review concurrency, human schedule and landing separately from permissions.
5. Validate selected profiles through no-edit smoke tasks in a disposable
   workspace under the confirmed host. Ask each to report only its identity and
   completion; compare requested/effective settings. Native settlement, release
   and cleanup must be verified. Do not mark a failed or unavailable launch
   validated or silently broaden its permissions. Use an isolated setup record;
   a smoke test grants no delivery brief/plan approval. Use `purpose:"setup"`
   and `approved.setup` with the concrete request/selected profiles as defined
   in [run records](../flyingnobita-deliver/references/run-record.md). Orca and
   Herdr smoke jobs use role `smoke` with each selected profile in turn.
6. Back up any existing project config. Write only approved project values,
   preserving unknown keys and unrelated host tables. Paseo profiles remain in
   Paseo; report required changes there rather than overwriting them. Keep
   legacy files and migration evidence while old runs may need them.
7. Add a concise pointer to `docs/agents/delivery.toml` in the repo's `AGENTS.md`
   only when requested or approved. The autonomous merge rule still requires
   the separate explicit consent in Deliver's project rules. Optional tracker
   setup is not a prerequisite to this skill.

Done when every required prerequisite is `ok` or named as a blocker, every
optional item was offered, settings are recorded, every selected profile has a
verified result or explicit blocker, and every setup resource is removed or
named as retained. Report the prerequisite table, changes, effective settings,
permissions, smoke evidence and migration decisions. Commit through
`flyingnobita-clean-commit`; publication is separate.
