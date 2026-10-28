# Delivery prerequisites

Check every row for the selected host, then report one table: component,
status (`ok`, `missing`, `degraded`, `skipped`), evidence, and the fix. Checks
are read-only. Install or change anything only after the user approves that
fix; a declined fix stays in the report.

A skill counts as installed when its `SKILL.md` exists in a skills directory
the delivering harness reads (`~/.agents/skills`, `~/.claude/skills`,
`~/.codex/skills`, or the target repo's `.agents/skills` / `.claude/skills`).
Deliver loads the prefixed names below. An unprefixed install (`grilling`
instead of `mattpocock-grilling`) is `degraded`: on a fleet host fix it with
`npx-skills-prefix apply`.

**Fleet host** means this dotfiles fleet: skills come from
`bootstrap/skill-seed.json` through `npx-skills-update`, apps from the
`.chezmoidata/` package files. Give the fleet fix first, then the upstream
link for anyone else.

## Required on every host

| Component | Check | Fix |
|---|---|---|
| `flyingnobita-clean-commit` | skill installed | Fleet: `chezmoi apply` deploys it from `dot_agents/skills/`. No upstream; without it Deliver cannot commit, so a miss blocks |
| Matt Pocock skills: `mattpocock-grilling`, `-tdd`, `-code-review`, `-pr`, `-diagnosing-bugs`, `-domain-modeling`, `-wizard`, `-writing-for-agents` | each installed | Fleet: `npx-skills-update`. Elsewhere: `npx skills add mattpocock/skills --skill <name> -g` from <https://github.com/mattpocock/skills>. A miss is `degraded`: Deliver runs the fallback in [dependencies](../../flyingnobita-deliver/references/dependencies.md) |
| `git` | `git --version`; target repo has a remote default branch | Install git through the host's package manager |
| `gh` | `gh auth status` succeeds for the account that will push | Fleet: in the package data file; `gh auth login`. <https://cli.github.com>. Needed to fork, push, open and merge PRs |
| Python 3.11+ | `python3 -c 'import tomllib'` | Fleet: mise `python`. Needed by `deliver-runtime` and project TOML |
| Bundled helpers | `python3 <deliver skill>/scripts/deliver-runtime.py select-host <<<'{}'` prints an `Error:` line, not a missing-file error; `deliver-orca-preflight.py` exists beside it | Reinstall the `flyingnobita-deliver` skill folder whole; the helpers ship inside it |

## Required per host

Check only the selected host's rows.

| Host | Component | Check | Fix |
|---|---|---|---|
| Herdr | `herdr` CLI | `herdr --version` | Fleet: mise `herdr` in the package data file. <https://github.com/herdrdev/herdr> |
| Herdr | `herdr` skill | installed where the target repo's agent reads it, or `herdr --skill` prints it | `npx skills add herdrdev/herdr --skill herdr -g`. On the fleet it is installed only repo-locally in `~/dotfiles`, so other repos rely on `herdr --skill` |
| Herdr | harness integration | `herdr integration status` shows each planned harness as `current` | `herdr integration install <harness>` for each. Codex skips untrusted hooks; on the fleet `scripts/common/codex-trust-hindsight-hooks` re-trusts them |
| Orca | Orca app and CLI | `orca --version` | Fleet: `orca-ide-bin` (Omarchy) or `stablyai/orca/orca` (macOS); gated to North-Omarchy and MBP-M4. <https://github.com/stablyai/orca> |
| Orca | `orca-orchestration` skill | installed | Fleet: deployed from `dot_agents/skills/` on gated hosts |
| Paseo | Paseo daemon and MCP tools | caller-bound Paseo MCP connection answers `list_profiles` | Fleet: `paseo-bin` (North-Omarchy). <https://github.com/getpaseo/paseo>. Never run the desktop `paseo` binary to probe |
| Paseo | profiles `planner`, `implementer`, `reviewer`, `qa` | all four in `list_profiles` | Fleet: `.chezmoidata/paseo.json`, then `chezmoi apply`. Elsewhere add them in Paseo |

## Optional

Present this section after the required checks, labelled **optional**: none of
it affects whether Deliver works. Recommend each missing item once with its
fix, and accept a no without follow-up.

| Component | When to offer | Check | Fix |
|---|---|---|---|
| Herdr Dagr | Herdr host only | `herdr plugin list --json` shows `herdr-dagr` | Recommend only, and say it is entirely optional: a DAG viewer pane for agent work in Herdr. Deliver does not drive it or publish graphs to it. Install and use it from <https://github.com/aemrebarut/herdr-dagr>; the fleet installs it on North-Omarchy and MBP-M4 |
| Planner extras: `mattpocock-research`, `-codebase-design`, `-prototype` | always | each installed | As the Matt Pocock row. Without them the planner works in plain terms |
| Input producers: `mattpocock-to-spec`, `-to-tickets` | always | each installed | As the Matt Pocock row. Lets Deliver take a spec or ticket graph as input |
| Tracker setup: `mattpocock-setup-matt-pocock-skills` | target repo lacks `## Agent skills` in `AGENTS.md` | skill installed; section present | Offer to run it; Deliver otherwise offers GitHub, a local file or none |
| Follow-up skills: `mattpocock-wayfinder`, `flyingnobita-deliver-retro` (needs `mattpocock-retro`) | always | each installed | As the matching rows above |
| Distinct reviewer harness | always | a second harness (`claude` or `codex`) is on `PATH` and authenticated | Install the other harness; a reviewer on the implementer's harness still works |
