# Changes

- Nov-11, 2026 - 08:26 PM +08 - Tell setup's prerequisite table that a harness session started before a Herdr integration loads reports no identity, so it must restart or supply its native session ID.

- Nov-11, 2026 - 08:26 PM +08 - Correct the Herdr Quick start: Codex has no `/deliver-setup` command and selects the setup skill from a plain request that names it and the settings.

- Nov-11, 2026 - 07:25 PM +08 - Run both Python regression suites in GitHub Actions on Python 3.11 for every pull request and every push to `main`, so a failing suite fails the check.

- Nov-11, 2026 - 04:54 PM +08 - Shorten the README title to Deliver skills, give the supported harnesses their own section, and reformat the role and skill tables.

- Nov-11, 2026 - 04:44 PM +08 - Give Deliver Retro a local environment-review procedure adapted from Matt Pocock's Retro, retaining attribution and MIT licensing; compare upstream guidance without invoking its user-only skill or requiring its installation.

- Nov-11, 2026 - 04:35 PM +08 - Explain Herdr profile inheritance when switching harnesses and direct setup to select compatible model, effort and mode values together.

- Nov-11, 2026 - 03:56 PM +08 - Recognize Matt Pocock tracker setup in either `AGENTS.md` or `CLAUDE.md`, and direct delivery Retro runtime tests to this repository's `tests/` directory.

- Nov-11, 2026 - 03:36 PM +08 - Replace the README's per-host harness table with a shared six-harness list and clarify that verification coverage varies by host and harness.

- Nov-11, 2026 - 03:24 PM +08 - Organize Quick start into collapsible Herdr, Orca and Paseo sections, with host-specific setup instructions and an updated first-delivery link; remove the licensing and usage-cost paragraph.

- Nov-11, 2026 - 03:22 PM +08 - Add a Herdr Quick start with Codex profile validation, usage-cost expectations and a small Python first-delivery example that ends on a local branch.

- Nov-11, 2026 - 03:18 PM +08 - Lead the README with turning a GitHub issue into reviewed code and choosing a different model for each delivery role.

- Nov-11, 2026 - 01:54 AM +08 - Release v0.2.0: Publish the delivery suite under the unprefixed names `deliver`, `deliver-setup`, `deliver-review` and `deliver-retro`, read Herdr role profiles from `[hosts.herdr.roles.<role>]`, and move legacy top-level Herdr role tables there through setup. Existing installs must remove and re-add the suite because the lock keys changed.

- Nov-11, 2026 - 01:43 AM +08 - Publish the four skills as `deliver`, `deliver-setup`, `deliver-review` and `deliver-retro`; existing installs must remove and re-add the suite because the lock keys change, and the suite still resolves the `flyingnobita-` prefixed names.

- Nov-11, 2026 - 01:50 AM +08 - Setup writes Herdr role profiles only as `[hosts.herdr.roles.<role>]` tables, and offers to move old top-level role tables there after showing the change, keeping every value, unknown key and unrelated table.

- Nov-11, 2026 - 01:42 AM +08 - Read Herdr role profiles from `[hosts.herdr.roles.<role>]` tables in `docs/agents/delivery.toml`, matching Orca; a file with only old top-level role tables still loads the same profiles with a warning that points to `deliver-setup` (or `flyingnobita-deliver-setup`).

- Nov-11, 2026 - 12:48 AM +08 - README now opens with the suite's purpose (Matt Pocock's skills across Herdr, Paseo and Orca, with per-role harness, model and effort) and lists the delivery roles.

- Nov-11, 2026 - 12:35 AM +08 - Rewrite the README in plain, terse prose: one install block, prerequisites as a flat list, run behavior stated directly, and a link to the full configuration reference.

- Nov-10, 2026 - 09:27 PM +08 - Release v0.1.2: The retro skill now checks the upstream retro contract in its own step 1, and its dependency fix type points at the delivery suite's real dependency record.

- Nov-10, 2026 - 08:13 PM +08 - Check the upstream retro contract inside the retro's own step 1: the presentation boundary and category overlap with the C and R checks are verified against the installed `retro`/`mattpocock-retro` when it loads, and the contract now lives with the retro skill instead of the delivery dependency record.

- Nov-10, 2026 - 08:13 PM +08 - Fix the Retro dependency fix type to point at the delivery suite's dependency record instead of a nonexistent file under the retro skill.

- Nov-10, 2026 - 05:03 PM +08 - Release v0.1.1: Align Herdr QA default profile with production (Codex gpt-6.1-sol/medium in auto mode) to eliminate drift before fleet cutover.

- Nov-10, 2026 - 04:48 PM +08 - Release v0.1.0 documentation repair: Ensure Orca executable resolution explicitly prevents bare orca GNOME screen reader collision across all entrypoints, and verify disposable local installation receipt.

- Nov-10, 2026 - 04:46 PM +08 - Allow native Orca orchestration guide directly without requiring a local discovery stub; document Orca executable resolution and public installation routes.

- Nov-10, 2026 - 04:42 PM +08 - Fix Skills CLI update documentation in README to use installed skill names and clarify branch-tip versus tagged release installation; update Orca prerequisite guidance to reference bundled orchestration install command and official URLs.

- Nov-10, 2026 - 04:30 PM +08 - Release v0.1.0: Publish the delivery suite as a standalone installable public repository covering Deliver, Setup, Review, and Retro. Refreshed skills from production dotfiles without orphaned dagr references; made identity, org access, and contribution routing portable; replaced mandatory personal commit dependencies with repository commit rules and optional custom commit skill support; added dual upstream/prefixed dependency resolution; removed private fleet pointers and paths; added README and MIT license; and adapted complete runtime and preflight test suites.

- Oct-28, 2026 - 11:45 AM +08 - Refer to Matt Pocock skills by their upstream names (`grilling`, `tdd`) instead of fleet-prefixed `mattpocock-*` names, and note how to tell `code-review` apart from a harness built-in.

- Oct-28, 2026 - 11:41 AM +08 - Copy the flyingnobita-deliver, -setup, -review and -retro skills and the helper tests from the dotfiles repo at ebe6374, as the future public source; dotfiles stays authoritative until the scheduled migration.
