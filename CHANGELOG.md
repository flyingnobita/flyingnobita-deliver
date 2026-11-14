# Changes

- Nov-14, 2026 - 03:40 PM +08 - Record Herdr and Orca worktree behavior from live checks: `deliver-implement` now passes `--branch` on Orca so a ticket's branch is exactly `<kaneo-key>-<slug>` instead of `<git-user>/<name>`; both hosts' removal keeps the branch for `git branch -d`; and closing a Herdr workspace first orphans the worktree, recoverable with `herdr worktree open`. Receipts are in `docs/quick-start-receipts/2026-11-14-herdr-worktree-cleanup.md` and `2026-11-14-orca-worktree-branch.md`.
- Nov-14, 2026 - 02:46 PM +08 - Make `deliver-implement` cleanup match each host: remove a ticket's workspace and worktree with the adapter's single removal call (never closing a Herdr workspace first), start each Paseo ticket from the target tip's SHA instead of `origin/<default>`, and track the branch Orca actually creates from `--name` so `git branch -d` targets it. Call each ticket's host view a workspace, as Herdr, Orca and Paseo do. The Paseo receipt is in `docs/quick-start-receipts/2026-11-14-paseo-base-branch.md`.
- Nov-13, 2026 - 11:58 PM +08 - Release v0.3.0: add `deliver-implement`, which builds agreed tickets in parallel implementer workers and lands each as linear history through a verified rebase; accept patch-equal landing rebases in `rebased` and `orca-rebased` and their verify steps; bound Herdr observation to one `wait` plus a fixed pane tail and pre-trust each worktree before dispatch; refuse an unproven effective profile; and record plan approval, test group kinds and gate-task closure before repair. Re-add the suite to install the fifth skill.
- Nov-13, 2026 - 12:15 AM +08 - Reword the README's "Already using Matt Pocock's skills?" table to say what replaces each command: `/grill-me` and `/grill-with-docs` map to the orchestrator's `grilling` and `domain-modeling`, the planner writes its own plan and tickets in place of `/to-spec` and `/to-tickets`, and `/implement` and `/implement-spec` split into the implementer's test-first build, the reviewer's `code-review` and the orchestrator's ticket graph.
- Nov-12, 2026 - 05:46 PM +08 - Let `deliver-implement` land a reported Orca ticket after the orchestrator's rebase: the runtime's new `orca-rebased` command records a clean rebase whose patch-ids equal the reported commits, and `orca-verify` accepts the rebased tip in contracts 1 and 2, so a moved target no longer costs an extra worker round. A two-ticket live Orca run landed the second ticket this way; the receipt is in `docs/quick-start-receipts/2026-11-12-orca-landing-rebase.md`.
- Nov-12, 2026 - 05:43 PM +08 - Give `deliver-implement`'s landing steps explicit Paseo branches: Paseo writes the claim, worker report, rebase receipt with patch-id comparison, verification output and end-of-run note to a private run directory instead of `report`/`rebased`/`verify`/`checkpoint`, and creates no runtime record. Validated live on Paseo with two disposable tickets, max 2 workers, an orchestrator rebase of the second ticket and archived workspaces.
- Nov-12, 2026 - 04:40 PM +08 - Point README readers who already have agreed tickets from `/to-tickets` to `deliver-implement`, which skips grilling and planning and runs `/implement` on each ticket in parallel.
- Nov-12, 2026 - 04:26 PM +08 - Let `deliver-implement` land a reported ticket after its own rebase: the runtime's new `rebased` command accepts a rebase whose patch-ids equal the reported commits, and `verify` and `followup` then accept the rebased tip, so a moved target no longer costs a worker round. A Herdr prompt that hits Herdr's 5 s `agent_prompt_stalled` check is now recorded as observed once the slow worker starts, instead of staying dispatch-uncertain. The skill also keeps red-proof probes out of the ticket worktree and checkpoints the run as `complete` or `blocked` at the end.
- Nov-12, 2026 - 03:51 PM +08 - Add an "Already using Matt Pocock's skills?" section before the README Quick start that maps each Matt Pocock skill to the role that runs it and names what `deliver` adds: a harness, model and effort per role, parallel ticket builds, a choice of Herdr, Paseo or Orca, and orchestrator checks between handoffs.
- Nov-12, 2026 - 03:34 PM +08 - Have each `deliver-implement` worker rebase onto the target tip and re-run its tests before reporting done, so conflicts with tickets that landed meanwhile are resolved in the worker's own session instead of costing the ticket its one repair retry; the orchestrator's landing rebase stays to catch tickets that land in between.
- Nov-12, 2026 - 03:12 PM +08 - Land `deliver-implement` tickets as linear history: the orchestrator rebases each ticket branch onto the target tip, verifies it, and fast-forwards the target, so `update-fleet publish` accepts the result instead of refusing a `merge <branch>` commit.
- Nov-12, 2026 - 02:55 PM +08 - Add `deliver-implement`, a fifth suite skill that implements agreed tickets in parallel implementer workers (one worktree each, within `max_workers` and ticket dependencies), verifies and merges each into the branch the user started on, notifies the user as soon as a ticket blocks, and cleans up; the runtime gains an `implement` run purpose that authorizes only the implementer role.
- Nov-12, 2026 - 12:28 PM +08 - Name every test group's kind in the plan, one of the contract's `behavioral`, `guard` or `bootstrap`, and plan a new public surface as `bootstrap` with a module-scope import and a plan-backed reason so its red is bootstrap absence rather than an import error (DLV-23).
- Nov-12, 2026 - 12:27 PM +08 - Record the plan approval at the plan stop, before any build task or attempt exists: the stop's done criterion now requires the `approve` call with `brief`, `plan` and `seams` and the actual request/approval as `evidence`, so the build no longer loses a dispatch cycle to `approved plan and seams or purpose-specific authorization required` (DLV-24).
- Nov-12, 2026 - 12:27 PM +08 - Close the finished gate task before dispatching repair: with `max_workers` reached, verifying or abandoning the completed review task is the step before opening the repair attempt, because the verified gate releases its worker slot first and the `concurrency limit reached` refusal is scheduling.md's rule (DLV-25).
- Nov-12, 2026 - 11:44 AM +08 - Treat one idle sample as unproven silence: `wait` settles `settled-no-report` only after two consecutive idle samples with no background work, because a worker flaps to idle between model turns and was reported settled mid-turn (DLV-22).
- Nov-12, 2026 - 12:59 AM +08 - Pre-trust each new Herdr worktree checkout for the planned harness and record the acknowledgement with `worktree-trust` before dispatch: `prompt` and `dispatch-intent` now refuse an attempt whose checkout and harness have no recorded trust, the adapter names the verified Claude and Codex trust stores, and raw text, keys or `/status` writes into a live worker pane are forbidden.
- Nov-12, 2026 - 12:54 AM +08 - Make the runtime `wait` the single completion observation: one call holds through background work and returns a bounded pane tail marked `tail_truncated` when the pane held more lines than returned or the 4000-character cap clipped it, the attempt's `waits` count refuses a third call, and the Herdr adapter stops chaining `herdr agent wait`, `agent get`, `agent read` and terminal input to poll a worker pane.
- Nov-12, 2026 - 12:52 AM +08 - Refuse a delivery report whose effective profile is missing, differently named or unequal to the requested profile: new runs must declare `observed_profile` in the canonical `harness`/`model`/`effort`/`mode` vocabulary, and verification rechecks it against the bound proof.
- Nov-12, 2026 - 12:51 AM +08 - Ask at the grilling stop whether the user wants the change activated locally before it ships, record the activation and restore steps in the brief and the approved plan before the ship stage, run them with a gate and a stop for the user's try-out, and treat activation work that starts during ship as a scope change (DLV-20).
- Nov-12, 2026 - 12:48 AM +08 - Bound Herdr pane observation to a status plus a fixed tail: every `agent read` passes `--lines` at or below 40, a wider read is replaced by a bounded source, report or worktree file, and worker reports keep one status line per check plus at most 20 lines of failing output.
- Nov-12, 2026 - 12:47 AM +08 - Require a second-rewrite variant in every stateful seam group's test: a second pass with an adjacent state that asserts what the first left and the order or retention limit the seam has, and reject a single-write behavioural group at the red check.

- Nov-11, 2026 - 11:21 PM +08 - Validate the Paseo Quick start against `a5cfdff` with a disposable repository and a first-time setup and delivery: tell the user to approve the session's Paseo workspace and agent creation, name the setup skill for Codex instead of a slash command, and stop setup from opening hidden background workspaces.

- Nov-11, 2026 - 10:44 PM +08 - Accept Orca's `run-current` response without runtime metadata in the caller preflight, so a Codex caller on Orca 1.4.256 is confirmed instead of reported broken.
- Nov-11, 2026 - 10:44 PM +08 - Stop passing a delivery request ID to `worker-start --retry-request`; Orca accepts only the native request UUID it reported, and the walkthrough's first planner smoke was rejected until the flag was omitted.
- Nov-11, 2026 - 10:30 PM +08 - Validate the Orca Quick start against `a87f495` with an isolated install and a disposable repository: name the setup skill in the Codex request instead of a slash command, and record the profile, setup and delivery evidence.
- Nov-11, 2026 - 09:54 PM +08 - Record the installed revision a retro ran at in its ledger entry and name the Skills CLI lock's live path, so a behaviour difference after an install update has a revision to compare.

- Nov-11, 2026 - 08:26 PM +08 - Tell setup's prerequisite table that a harness session started before a Herdr integration loads reports no identity, so it must restart or supply its native session ID.
- Nov-11, 2026 - 08:26 PM +08 - Correct the Herdr Quick start: Codex has no `/deliver-setup` command and selects the setup skill from a plain request that names it and the settings.
- Nov-11, 2026 - 07:38 PM +08 - Verify the installed delivery suite against `a5cfdff`: record the pre-update inventory, recovery snapshot, per-installation revisions and gaps, name the prefix tooling's superseded lock path, and report the Retro run that overlapped the install window.
- Nov-11, 2026 - 07:33 PM +08 - Give each retro environment category a stable `E1` to `E7` ID for ledger coverage and recurrence matching, record the compared upstream retro revision in the ledger, and document the compressed Codex rollout, Herdr session matching and bounded-timestamp fallbacks the evidence step needs.

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
