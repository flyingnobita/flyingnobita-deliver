# Herdr worktree branch and cleanup - 2026-11-14

Receipt for the `herdr worktree` behavior `deliver-implement` relies on.
Herdr 0.9.5 (client and server), run from a Claude Code session in a Herdr pane
on `north-omarchy`, against a disposable repo with one commit on `main`.

## Create

`herdr worktree create --cwd REPO --branch dlv-26-greet-helper --base main
--path PATH --no-focus` created branch `dlv-26-greet-helper` exactly as given,
plus workspace `w1K` with one tab and root pane.

When no workspace was open on the source repo, Herdr also opened one (`w1J`)
and reported it as `source_workspace_id`. In a delivery run the orchestrator's
own workspace is normally that source.

## Remove

After a commit in the worktree and `git merge --ff-only` on `main`,
`herdr worktree remove --workspace w1K` returned `worktree_removed`
(`forced: false`). The directory, the Git registration and the workspace were
gone; the branch remained, and `git branch -d` deleted it.

## Closing the workspace first

`herdr workspace close` on a fresh worktree workspace succeeded, then
`herdr worktree remove --workspace <id>` failed with `workspace_not_found` and
left the worktree directory and registration behind.
`herdr worktree open --cwd REPO --path PATH --no-focus` returned a new
workspace, and removing that one cleaned up normally.

## Not covered

Forced removal, dirty worktrees, and Herdr versions other than 0.9.5.
