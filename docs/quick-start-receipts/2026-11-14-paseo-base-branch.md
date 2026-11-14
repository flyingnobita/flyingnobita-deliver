# Paseo base branch and archive cleanup - 2026-11-14

Receipt for the `create_workspace` `baseBranch` forms and `archive_workspace`
cleanup that `deliver-implement` relies on. Paseo 0.15.4, server
`srv_EwtiHqRCFBCw`, run by a Paseo agent on `north-omarchy`.

## Fixture

A disposable repo with a bare `origin`: commit A pushed, commit B on local
`main` only, and a never-pushed branch `target` at B.

- A = `25f86544f55f4de1009f479f599f1524f291e31c` (`origin/main`)
- B = `dc3127ad2d3add9c31cfcb445ad1b46f5395a7a5` (`main`, `target`)

## Base branch

Every call used `isolation: worktree`, `mode: branch-off` and succeeded.

| Test | baseBranch | Worktree HEAD |
| --- | --- | --- |
| T1 | `origin/main` | A |
| T2 | `main` (ahead of origin) | B |
| T3 | `target` (never pushed) | B |
| T4 | full SHA of B | B |

Paseo resolves a local branch name or SHA locally and does not rewrite it to
`origin/<branch>`.

## Archive cleanup

`archive_workspace` returned `removedDirectory: true` for all four. Afterwards
no worktree registration or directory remained, `git worktree prune` changed
nothing, and each branch remained until `git branch -d` deleted it.

The 2026-11-12 Paseo receipt pruned stale registrations after archiving; this
run found none, so that step is not needed on 0.15.4.

## Not covered

Error cases, PR and checkout modes, and Paseo versions other than 0.15.4.
