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
4. Squash-merge and delete the remote branch.
5. Remove the work's workspace if the run created it, fast-forward the local default branch, and verify it equals the merged commit on the remote. A reused workspace is your own: keep it and its branch, and name both in the final report for the user to archive.
6. Delete the local work branch of a created workspace once `git diff --quiet <branch> <default>` shows its tree equals the default branch. A squash merge leaves the branch unmerged by ancestry, so this tree check is the evidence; a differing tree is a blocker to report.

Done when the local default branch equals the remote merged commit and no work branch or created workspace remains.

## Upstream repo

1. Squash the branch's unpublished commits into one following repository commit rules (or a configured custom commit skill), so the upstream PR carries one commit. Re-run the full suite on the result.
2. Show the user the PR draft: title, body, base, head. This is a stop.
3. On the user's OK, push to the fork, verify the remote ref, and open the PR against the upstream base branch.

Done when the PR exists and its head commit equals the pushed commit. Leave the workspace in place for review follow-ups.
