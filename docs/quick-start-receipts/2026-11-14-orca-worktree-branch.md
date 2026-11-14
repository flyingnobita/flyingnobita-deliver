# Orca worktree branch and cleanup - 2026-11-14

Receipt for the `orca worktree` behavior `deliver-implement` relies on.
Orca 1.4.258, run by an Orca agent on `north-omarchy` against a disposable repo
with one commit on `main`, registered with `orca repo add` (a `path:` selector
does not resolve an unregistered repo).

## Create

Each call was `orca worktree create --repo path:<repo> --name <name>
--base-branch main --json`, plus `--branch` where shown.

| Test | `--name` | `--branch` | Branch created |
| --- | --- | --- | --- |
| O1 | `dlv-26-greet-helper` | none | `flyingnobita/dlv-26-greet-helper` |
| O2 | `t2` | none | `flyingnobita/t2` |
| O3 | `o3` | `dlv-27-explicit` | `dlv-27-explicit` |

Without `--branch`, the prefix is the repo's Git user, and a taken name gets a
numeric suffix. Checkouts land in `~/orca/workspaces/<repo-name>/<name>`.

## Remove

After a commit in each worktree and `git merge --ff-only` on `main`,
`orca worktree rm --worktree id:<id> --json` (no force) returned
`removed: true`. The checkout and its registration were gone; each branch
remained, and `git branch -d` deleted it.

The Orca window showed "Branch auto-name failed ... Generation timed out after
60s" for `naga`, the UI-created worktree whose agent ran this test, not for any
test worktree. Orca tries to rename a UI worktree's placeholder branch from its
first agent message; on timeout the branch keeps its placeholder
(`flyingnobita/naga`). The 2026-11-12 Orca receipt's CLI-named branches kept
their names after workers ran.

## Not covered

Removing an unmerged branch, `--branch` name collisions, and remote hosts.
