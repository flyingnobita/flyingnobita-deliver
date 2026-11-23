# Ship

Read [configuration.md](configuration.md) for the run's landing choice.
A partial run returns through scope approval before shipping. Preserve existing
repository requirements for publishing skills and authorization; a profile or
legacy config value grants neither publication nor deployment permission.
A local preview is finished before this stage; activation work that starts here
is a scope change, not a shipping step.

For `leave`, finish local commits and verification, report the branch and
retained workspace, then stop. For `pr`, follow the applicable PR approval path
below but stop after the verified PR head; retain the workspace and never merge.
`standard` follows the full applicable branch below.

## Both repo routes

Before documentation closeout, give the implementer a claim matrix: exact command,
execution mode, version, observed outcome, retained receipt and unqualified
variants. Review README, release notes, compatibility and evidence against it.
Installation, startup, authentication, model execution and enforcement are
separate claims; deploying task shims does not prove their commands execute.

After authorized publication, check the actual destination repository/ref and
refresh proposed/unpublished source-install instructions. Verify that command
in disposable installation state before marking it supported. Distinguish source
publication from a tagged GitHub Release or deployed installation. For `leave`,
describe the local state accurately and retain publication-dependent checks as gaps.

Follow repository commit rules and explicit authority. A delivery run commits
only owned changes to the work branch; pushing, PR opening, and merging require
explicit repository consent or session approval.

1. The work is already committed: rules and docs after the plan stop, the implementation and review fixes by the implementer role. Commit any remaining owned change following repository commit rules (or a configured custom commit skill), which reads the repo's message style and changelog rules. Reference the issue in a footer when one exists (`Fixes #N`).
2. Write the PR title and body with `pr` (or `mattpocock-pr`). Where the repo has a PR template, fill the template and fold the summary and evidence into it. Include the mention-in-PR review findings and any alternative the user asked to offer.

## Direct repo

The repo's `AGENTS.md` merge rule or explicit session approval authorizes merging (see [project-rules.md](project-rules.md)). Write access alone never grants merge authority; branch protections must be respected. It applies once every check before it has passed: the full suite and linters after the last code edit, a clean review, and QA when it ran.

1. Push the branch and verify the remote branch ref equals the local `HEAD`.
2. Open the PR against the default branch.
3. For `pr`, or when merge authority is absent, report the PR and verified head and retain the workspace. Otherwise, if authorized to merge, wait for any required status checks; a failure goes back through the pipeline as a red-green fix.
4. Squash-merge and never pass `--delete-branch` (`gh pr merge <n> --squash`), then record the merged commit on the remote default branch. gh reads `--delete-branch` as "delete the branch everywhere": it also deletes every worktree that has the branch checked out, so a created workspace loses its path and its local branch before cleanup reaches it, and the host's worktree removal then has nothing to remove while its panes point at a deleted cwd (observed 2026-11-14 from the main checkout on PR flyingnobita/agent-profiles#49).
5. Fast-forward the local default branch and verify it equals the merged commit on the remote, then confirm the branch's tree equals the default branch with `git diff --quiet <branch> <default>`. Run this check while the remote work branch still exists: a squash merge leaves the branch unmerged by ancestry, so the tree equality is the only evidence it landed, and a differing tree is a blocker to report before anything is deleted.
6. Remove the created workspace through the host adapter and verify it is gone (`git worktree list` shows no path for it and the adapter reports the removal). A reused workspace is your own: keep it and its branch, and name both in the final report for the user to archive.
7. Delete the remote work branch of a created workspace only after step 6 confirmed the workspace is gone, with an explicit remote-only deletion (`git push <remote> --delete <branch>`) that touches no local ref or worktree. Verify the remote ref is gone with `git ls-remote --heads <remote> <branch>` returning no row; a surviving row is a blocker to report. A repository that already auto-deletes head branches reports the branch as absent here and needs no push.
8. Delete the local work branch with `git branch -D <branch>`, gated on step 5's tree check: `-d` refuses a branch squash-merged without ancestry.

Done when the local default branch equals the remote merged commit and, for a created workspace, no workspace or work branch remains locally or on the remote; a reused workspace and its branch are kept and named instead.

## Upstream repo

1. Squash the branch's unpublished commits into one following repository commit rules (or a configured custom commit skill), so the upstream PR carries one commit. Re-run the full suite on the result.
2. Show the user the PR draft: title, body, base, head. This is a stop.
3. On the user's OK, push to the fork, verify the remote ref, and open the PR against the upstream base branch.

Done when the PR exists and its head commit equals the pushed commit. Leave the workspace in place for review follow-ups.
