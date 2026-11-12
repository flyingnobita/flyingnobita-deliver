---
name: deliver-implement
description: Implement agreed tickets in parallel implementer workers on Orca, Herdr or Paseo, one worktree per ticket, then land each on the target branch as linear history and clean up. Use when the user asks to implement tickets or issues (`implement 1,2,3`, `DLV-26`) or names `deliver-implement` (or `flyingnobita-deliver-implement`).
---

# Implement tickets

You are the **orchestrator**. The tickets are the agreed spec: there is no
brief, grilling, plan, reviewer role or QA. Each ticket gets its own worktree,
branch and implementer worker running `implement` (or `mattpocock-implement`);
you verify each result yourself and fast-forward the target branch to it, one
ticket at a time.

Run to completion without asking, except where a step below names a stop. When
a ticket **blocks**, notify the user at once and keep landing independent
tickets. The final report is the user's notification that the run is done.

Use the shared delivery files, resolved from this skill's directory:
[host detection](../deliver/references/host-detection.md), the selected adapter
in [adapters](../deliver/adapters/),
[configuration](../deliver/references/configuration.md),
[run records](../deliver/references/run-record.md) and
[scheduling](../deliver/references/scheduling.md). Run the
[runtime helper](../deliver/scripts/deliver-runtime.py) as `python3 <its path>`.

## 1. Resolve the run

1. **Host:** follow host detection and select one adapter. A host named in the
   request is used only when that session is confirmed; otherwise stop with the
   failed check.
2. **Tickets:** resolve each reference, a GitHub issue (`26`, `#26`) or Kaneo
   key (`DLV-26`), to both identities (`kaneo task list -p <PROJECT> --all`)
   and read it fully, with its "Blocked by" edges and GitHub issue
   dependencies. Name every ticket as `DLV-26 (#26)` when a Kaneo board
   exists. An ambiguous reference is a stop.
3. **Graph:** reject cycles. A blocker that is closed or merged is satisfied; a
   blocker outside the requested set and still open is a stop.
4. **Target branch:** a branch named in the request, else the current branch of
   your checkout. Record its name and SHA and state both in your first status
   line. Detached HEAD or a remote-tracking ref is a stop.
5. **Settings:** resolve per configuration, using only the **implementer**
   role and these keys: `max_workers` (default 3, capped by any host limit) and
   `human_schedule` (default `normal`). A worker count or schedule in the
   request overrides them.
6. **Model:** the request's override (harness, model, effort, and mode on
   Herdr; a profile ID on Paseo), else the project implementer role, else the
   adapter default. Validate it the adapter's way, passing only the
   implementer table. An override that is unclear, unknown or fails validation
   is a stop before anything is created: show what you parsed, why it failed,
   and the presets (project role, adapter default, Paseo profile IDs) to choose
   from.
7. **Human steps:** a human ticket, or a human step inside an agent ticket, is
   scheduled by `human_schedule` as in scheduling. Load `wizard` (or
   `mattpocock-wizard`) for each one and notify the user with the script path
   when it becomes ready. Its dependents wait until the user reports it done.
8. **Run record:** `create` with `purpose: "implement"`, the resolved
   `concurrency`, the implementer profile and the target branch as `base`, then
   `approve` with `approved.tickets` holding the ticket list and the user's
   request as `evidence`.
9. **Baseline:** run the full suite and linters on the target tip as the repo
   defines them. A failing baseline is a stop.

Done when the run record is approved and the baseline is green.

## 2. Dispatch

The **frontier** is every ticket whose blockers have landed or were already
satisfied. While a worker slot is free, take the next frontier ticket in the
request's order:

1. **Claim** it: set the repo's in-progress `status:` label when the repo uses
   status labels (only you change statuses).
2. Create its workspace through the adapter, branched from the target's current
   tip, on a branch named `<kaneo-key>-<slug>` (else `<issue>-<slug>`).
3. Start one implementer worker in it with: the ticket reference, the command
   to run `implement` (or `mattpocock-implement`) for that ticket alone, the
   repo's commit rules (or the configured `commit_skill`), a `Fixes #N` footer
   for a GitHub issue, the target branch name, and a last step before
   reporting: `git rebase <target>` onto its current tip, resolve any
   conflict, and re-run the tests. Its report: commits, the target SHA it
   rebased onto, and test and lint commands with one status line each.

Refill the frontier each time a ticket lands.

## 3. Land each finished ticket

Land one ticket at a time, keeping the target's history **linear**: no merge
commits, so a later publish accepts the range.

1. In the ticket's worktree, with its worker finished and the tree clean, run
   `git rebase <target-sha>`. On a conflict run `git rebase --abort`.
2. Confirm `git rev-list --merges <target-sha>..<branch>` is empty, then run the
   full suite and linters there yourself. A conflict, a merge commit or a
   failure goes back to the ticket's worker once, with the receipt: it rebases
   its branch onto the new target tip, resolves any conflict and re-runs its
   tests. Repeat steps 1-2 on its next report. A second failure **blocks** the
   ticket.
3. Fast-forward the target to the rebased branch tip. When the target is
   checked out, run `git merge --ff-only <branch>` in that checkout; git
   refuses rather than overwrite local changes, and that refusal blocks the
   ticket. Otherwise run
   `git update-ref refs/heads/<target> <branch-sha> <target-sha>`.
4. Set the repo's done or review `status:` label. Leave the issue open: its
   `Fixes #N` footer closes it when the user publishes.
5. Clean up through the adapter: close the worker and its window, remove the
   worktree, then `git branch -d <branch>`, which succeeds because the target
   now contains the branch.

When a ticket **blocks**, notify the user through the adapter's notify
operation with the ticket, the failed command and receipt, and its worktree and
window. Keep both, hold its dependents, and continue independent tickets. Check
the ticket again at each later wait; once the user reports a fix, land it from
step 1. A ticket the user drops is recorded as abandoned with their words as
evidence; its dependents stay blocked.

Done when every ticket has landed, is blocked, or is abandoned.

## 4. Report

Report: the target branch and its final SHA; each ticket as landed (its
commit range), blocked (reason, kept worktree and window) or abandoned; the requested
and effective implementer profile; the verification commands you ran; and the
issues that close on publish. Nothing is pushed: publishing is a separate
request. Suggest `deliver-review` (or `flyingnobita-deliver-review`) on the
landed range when the combined change warrants it, such as tickets that touched
the same module or a ticket the user fixed by hand.
