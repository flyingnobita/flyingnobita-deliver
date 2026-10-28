# Paseo adapter

Use the Paseo MCP tools for every operation. The `paseo` CLI on desktop installs is the Electron app binary and can open extra app windows, so leave it alone.

Read [configuration](../references/configuration.md) for shared concurrency,
human scheduling and landing settings. Keep the existing live profiles below.

## Roles

| Role | Profile id |
|---|---|
| planner | `planner` |
| implementer | `implementer` |
| reviewer | `reviewer` |
| qa | `qa` |

Read the profiles with `list_profiles` at setup. A missing profile is a blocker: tell the user which one and stop. Materialize a profile into `create_agent`:

- `provider`: `<provider>/<model>`;
- `settings.modeId`: `modeId`;
- `settings.thinkingOptionId`: `thinkingOptionId`;
- `settings.features`: `featureValues`.

Omit absent values.

## Operations

| Operation | Paseo |
|---|---|
| Create a workspace | `create_workspace` with `isolation: worktree`, `mode: branch-off`, `path` = repo root, `branchName`, and an explicit `baseBranch` (`origin/<default>` for an own repo, `upstream/<default>` for an upstream repo). It registers the project; keep the returned `workspaceId` and `cwd`. |
| Start a role | `create_agent` with the materialized profile, `workspaceId`, a title `<Role>: <work>`, and the role brief as `initialPrompt`. Leave `notifyOnFinish` at its default. |
| Send a follow-up | `send_agent_prompt` to the same role agent, so it keeps its context. |
| Wait for an event | Do nothing: finish, error and permission notifications arrive on their own. When a notification's response is truncated, read the rest with `get_agent_activity`. |
| Answer a permission | `respond_to_permission` (rule below). |
| Notify the user | End your turn; Paseo marks the workspace as needing attention. |
| Remove a workspace | `archive_workspace`; it archives the role agents and removes the Paseo-owned worktree. |

## Planner output

The planner profile runs in plan mode and finishes with an `ExitPlanMode` permission request whose payload holds the plan (`planText`, `planFilePath`). Read the plan from it, then answer `deny` with the message "Plan received; the orchestrator runs implementation". Approving it would turn the planner into an implementer.

## Permission rule

Approve a role's request when both hold:

- its working directory is the work's workspace;
- it only reads or checks: test runs, linters and format checks, reading files, and the dependency or tool caches those commands use outside the workspace.

Leave every other request pending (pushes, deletions, network writes, other hosts, paths outside the workspace) and tell the user which role asked for what. The user answers it in the Paseo app.
