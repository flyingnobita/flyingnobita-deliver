# Delivery prerequisites

Check every row for the selected host, then report one table: component,
status (`ok`, `missing`, `degraded`, `skipped`), evidence, and the fix. Checks
are read-only. Install or change anything only after the user approves that
fix; a declined fix stays in the report.

A skill counts as installed when its `SKILL.md` exists in a skills directory
the delivering harness reads (`~/.agents/skills`, `~/.claude/skills`,
`~/.codex/skills`, or the target repo's `.agents/skills` / `.claude/skills`).
Matt Pocock skills are checked under either their upstream names (`grilling`,
`tdd`) or fleet-prefixed names (`mattpocock-grilling`, `mattpocock-tdd`). Where
an upstream name collides with a harness built-in, such as Claude Code's
`code-review`, check that the installed `SKILL.md` comes from `mattpocock/skills`.

## Required on every host

| Component | Check | Fix |
|---|---|---|
| Commit capability | Git identity configured (`git config user.name`, `user.email`); if a custom commit skill is configured in `delivery.toml`, that skill is installed | Configure `git config user.name` and `user.email`. If a custom commit skill is specified in `delivery.toml`, install it; otherwise safe built-in commit behavior is used |
| Matt Pocock skills: `grilling`, `tdd`, `code-review`, `pr`, `diagnosing-bugs`, `domain-modeling`, `wizard`, `writing-for-agents` (or `mattpocock-*` prefixed) | each installed under either name | Install via `skills add mattpocock/skills --skill <name> -g` from <https://github.com/mattpocock/skills>. A miss is `degraded`: Deliver runs the fallback in [dependencies](../../flyingnobita-deliver/references/dependencies.md) |
| `git` | `git --version`; target repo has a remote default branch | Install git through the host's package manager |
| `gh` | `gh auth status` succeeds for the account that will push | Install GitHub CLI (<https://cli.github.com>) and run `gh auth login`. Needed to fork, push, open and merge PRs |
| Python 3.11+ | `python3 -c 'import tomllib'` | Install Python 3.11+. Needed by `deliver-runtime` and project TOML |
| Bundled helpers | `python3 <deliver skill>/scripts/deliver-runtime.py select-host <<<'{}'` prints an `Error:` line, not a missing-file error; `deliver-orca-preflight.py` exists beside it | Reinstall the `flyingnobita-deliver` skill folder whole; the helpers ship inside it |

## Required per host

Check only the selected host's rows.

| Host | Component | Check | Fix |
|---|---|---|---|
| Herdr | `herdr` CLI | `herdr --version` | Install `herdr` from <https://github.com/herdrdev/herdr> |
| Herdr | `herdr` skill | installed where the target repo's agent reads it, or `herdr --skill` prints it | Install via `skills add herdrdev/herdr --skill herdr -g`, or configure `herdr --skill` |
| Herdr | harness integration | `herdr integration status` shows each planned harness as `current` | `herdr integration install <harness>` for each, including `omp` and `opencode` |
| Orca | Orca app and CLI | `ORCA --version` from resolved executable (`ORCA_CLI_COMMAND` if set; `orca-dev` in dev context; `orca-ide` on Linux outside managed terminal, never bare `orca`; otherwise `orca`) | Install Orca from <https://github.com/stablyai/orca> or <https://www.onorca.dev> (macOS: `brew install --cask stablyai/orca/orca`, Arch: `stably-orca-bin` or `orca-ide-bin`) |
| Orca | Orchestration guide | `orca-orchestration` skill installed, OR `ORCA skills get orchestration --full` succeeds from the resolved Orca CLI | Native guide is bundled with Orca (`ORCA skills get orchestration --full`). A missing local discovery stub does not block if the native guide is available from the CLI |
| Paseo | Paseo daemon and MCP tools | caller-bound Paseo MCP connection answers `list_profiles` | Install Paseo from <https://github.com/getpaseo/paseo>. Never run the desktop `paseo` binary to probe |
| Paseo | profiles `planner`, `implementer`, `reviewer`, `qa` | all four in `list_profiles` | Add the four role profiles in Paseo |

For OpenCode V2, a current integration is necessary but insufficient: use the
[full-TUI session-bound launch](../../flyingnobita-deliver/references/opencode-launch.md).
Mini/headless clients do not run the native reporter. Verify session identity and
working/completion in the no-edit smoke; a model reply alone does not pass.

## Optional

Present this section after the required checks, labelled **optional**: none of
it affects whether Deliver works. Recommend each missing item once with its
fix, and accept a no without follow-up.

| Component | When to offer | Check | Fix |
|---|---|---|---|
| Herdr Dagr | Herdr host only | `herdr plugin list --json` shows `herdr-dagr` | Recommend only, and say it is entirely optional: a DAG viewer pane for agent work in Herdr. Deliver does not drive it or publish graphs to it. Install and use it from <https://github.com/aemrebarut/herdr-dagr> |
| Planner extras: `research`, `codebase-design`, `prototype` (or `mattpocock-*` prefixed) | always | each installed under either name | As the Matt Pocock row. Without them the planner works in plain terms |
| Input producers: `to-spec`, `to-tickets` (or `mattpocock-*` prefixed) | always | each installed under either name | As the Matt Pocock row. Lets Deliver take a spec or ticket graph as input |
| Tracker setup: `setup-matt-pocock-skills` (or `mattpocock-setup-matt-pocock-skills`) | target repo lacks `## Agent skills` in `AGENTS.md` | skill installed under either name; section present | Offer to run it; Deliver otherwise offers GitHub, a local file or none |
| Follow-up skills: `wayfinder` (or `mattpocock-wayfinder`), `flyingnobita-deliver-retro` (needs `retro` or `mattpocock-retro`) | always | each installed under either name | As the matching rows above |
| Distinct reviewer harness | always | a second harness (`claude` or `codex`) is on `PATH` and authenticated | Install the other harness; a reviewer on the implementer's harness still works |
