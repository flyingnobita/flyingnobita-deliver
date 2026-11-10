# Delivery workflow guide

Use `deliver` (or `flyingnobita-deliver`) for a description, issue, spec or ticket graph.
It confirms a brief, checks the baseline, settles open decisions, gets a plan
and test seams approved, then builds, independently verifies, reviews, optionally
tests in the real environment, and ships within the approved authority.

- `deliver-setup` (or `flyingnobita-deliver-setup`): configure profiles and
  project defaults or migrate the old Orca configuration. Normal entry does not
  require prior setup.
- `deliver-review` (or `flyingnobita-deliver-review`): review and repair an
  existing branch without starting a delivery or publishing it.
- `/deliver-retro` (or `/flyingnobita-deliver-retro`): user-invoked
  retrospective on one or more runs; finds coordination and role-split losses
  and proposes fixes to this skill.
- [Configuration](configuration.md): concurrency, scheduling, landing and host
  settings. Paseo profiles stay in Paseo; Herdr and Orca have separate settings.
- [Scheduling](scheduling.md): human work, ticket states, partial runs and resume.
- [Migration](migration.md): replacements for `orch-*` and existing-run safety.

The initiating session stays the orchestrator. Each adapter requires verified
caller membership; installation or matching cwd is insufficient. Read
[host detection](host-detection.md) and the selected adapter before diagnosing
a launch or recovery problem. A stopped process and a lost connection require
different actions. Reports remain outside disposable worktrees.

The pipeline's source of truth is [pipeline.md](pipeline.md), and publication
authority is defined in [ship.md](ship.md) and the repo's own rules. A role's
success report does not independently verify a stage. "Wrap up" reports a
partial run; it does not authorize shipping an incomplete original scope.
