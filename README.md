# flyingnobita-deliver skills

Runs [Matt Pocock's skills](https://github.com/mattpocock/skills) (`grilling`, `tdd`, `code-review`, `pr` and the rest) across a team of coding agents. It works on three agent hosts, [Herdr](https://herdr.dev), [Paseo](https://paseo.sh) and [Orca](https://www.onorca.dev), and each role can run on its own harness (Claude Code, Codex and so on), model and effort level. A delivery goes from brief to merged code, and the orchestrator re-checks every agent's work before it ships.

## Roles

- **Orchestrator:** your own session, in Claude Code or Codex (Orca also accepts Antigravity). Grills you on the brief, starts the other roles, checks their evidence and ships.
- **Planner:** reads the code and the agreed brief, then splits the work into ordered slices. Read-only.
- **Implementer:** builds each slice test-first and commits.
- **Reviewer:** reviews the branch against the repo's standards and the spec.
- **QA:** tests the change in a live environment, when you ask for it.

Each role except the orchestrator gets its own profile. For example:

| Role | Harness | Model | Effort |
|---|---|---|---|
| Planner | `claude` | `claude-opus-5-5` | `high` |
| Implementer | `pi` | `opencode-go/deepseek-v4.1-flash` | `high` |
| Reviewer | `codex` | `gpt-6.1-sol` | `low` |
| QA | `codex` | `gpt-6.1-sol` | `low` |

Supported harnesses by host:

| Host | Harnesses |
|---|---|
| Herdr | `claude`, `codex`, `agy`, `pi`, `omp`, `opencode` |
| Orca | any agent Orca can launch, such as `claude`, `codex` and `pi` |
| Paseo | your Paseo agent profiles named `planner`, `implementer`, `reviewer` and `qa`, each with its own provider and model |

## Skills

| Skill | What it does | How to run it |
|---|---|---|
| [`deliver`](skills/deliver/SKILL.md) | Runs a full delivery | `deliver <input>` (issue URL, `#N`, spec or brief) |
| [`deliver-setup`](skills/deliver-setup/SKILL.md) | Checks prerequisites, configures role profiles, validates hosts | `/deliver-setup` |
| [`deliver-review`](skills/deliver-review/SKILL.md) | Reviews and repairs an existing branch against standards and spec | `/deliver-review` |
| [`deliver-retro`](skills/deliver-retro/SKILL.md) | Looks back over past runs and proposes fixes to the skills and profiles | `/deliver-retro` |

The `flyingnobita-` prefix is a fleet convention, not part of these names. Fleet installs still see `flyingnobita-deliver`, `flyingnobita-deliver-setup` and so on, and the suite resolves both forms.

## Install

With the [Skills CLI](https://github.com/vercel-labs/skills) (`skills`, or `npx skills`):

```bash
skills add flyingnobita/flyingnobita-deliver -g   # global
skills add flyingnobita/flyingnobita-deliver      # current project only
```

This installs from `main`. To pin a release, add the tag:

```bash
skills add flyingnobita/flyingnobita-deliver#v0.1.2 -g
```

To update, pass the installed skill names, not the repo slug:

```bash
skills update deliver deliver-setup deliver-review deliver-retro -g
```

If you installed the older prefixed names, remove and re-add the suite instead: the lock keys changed (see the CHANGELOG).

`skills update -g` updates everything, and rerunning `skills add ... -g -y` reinstalls from the tip of `main`.

## Usage

Start a session inside Herdr, Paseo or Orca, then type `deliver` followed by an issue, a spec or a plain description:

```text
deliver #42
deliver https://github.com/owner/repo/issues/42
deliver add a --dry-run flag to the sync command
```

It asks you questions about the brief, waits for you to approve a plan, then builds, reviews and ships. You get a report at the end.

## Prerequisites

- Linux or macOS
- `git` with `user.name` and `user.email` set
- [`gh`](https://cli.github.com), logged in with `gh auth login`
- Python 3.11+ (standard library only)
- At least one delivery host:
  - Herdr
  - Paseo
  - Orca: `brew install --cask stablyai/orca/orca` on macOS, `stably-orca-bin` or `orca-ide-bin` on Linux. On Linux outside an Orca terminal, call the CLI as `orca-ide`. Bare `orca` starts the GNOME screen reader.
- Matt Pocock's skills: `skills add mattpocock/skills -g`. The suite uses `grilling`, `tdd`, `code-review`, `pr`, `diagnosing-bugs`, `domain-modeling`, `wizard` and `writing-for-agents`, and also finds them under a `mattpocock-` prefix.

`/deliver-setup` checks all of this.

## How a run works

1. Intake: turn the input into a brief.
2. Setup: create the workspace and record a baseline.
3. Grilling: settle every open question with you.
4. Plan: the planner proposes slices and you approve them.
5. Build: the implementer builds each slice test-first.
6. Review: the reviewer checks standards and spec until clean.
7. QA: test the change in a live environment, if you asked for it.
8. Ship: merge directly, or open a PR on an upstream repo.
9. Report: summarize the evidence and update the issue tracker.

The run stops for you at the grilling round, plan approval, any scope change, steps only you can do (credentials, CI secrets), and the PR draft for an upstream repo. Everything else runs unattended.

The orchestrator doesn't trust agent reports. It reruns the tests, confirms new tests fail on the base commit, runs the linters and checks review findings itself.

Having write access isn't enough to merge. A direct merge needs the autonomous delivery rule in the repo's `AGENTS.md` or your approval in the session, and branch protection always applies.

Commits follow the target repo's conventions. Set `commit_skill` to use your own commit skill instead, such as `flyingnobita-clean-commit`.

## Configuration

Optional, in `docs/agents/delivery.toml`. The `[delivery]` table works on every host:

```toml
[delivery]
max_workers = 3
human_schedule = "normal" # normal | front-load | back-load
landing = "standard"      # standard | leave | pr
commit_skill = ""         # optional custom commit skill name
```

Role profiles are set differently on each host. Every setting and value is explained in [configuration.md](skills/deliver/references/configuration.md).

### Orca

To set the roles to the profiles in the table above, add a `[hosts.orca.roles.<role>]` table per role:

```toml
[hosts.orca.roles.planner]
harness = "claude"
model = "claude-opus-5-5"
effort = "high"

[hosts.orca.roles.implementer]
harness = "pi"
model = "opencode-go/deepseek-v4.1-flash"
effort = "high"

[hosts.orca.roles.reviewer]
harness = "codex"
model = "gpt-6.1-sol"
effort = "low"

[hosts.orca.roles.qa]
harness = "codex"
model = "gpt-6.1-sol"
effort = "low"
```

`model` and `effort` are optional; leave them out to use Orca's defaults, but `effort` needs an explicit `model`. A role table you set replaces that role's [default](skills/deliver/references/orca-profiles.toml) whole.

### Herdr

Use top-level role tables. Each takes `harness`, `model`, `effort` and `mode`:

```toml
[planner]
harness = "pi"
model = "opencode-go/kimi-k3.1-pro"
effort = "high"
mode = "default"

[qa]
harness = "codex"
model = "gpt-6.1-sol"
effort = "medium"
mode = "auto"
```

Fields you set are merged over the [defaults](skills/deliver/references/herdr-profiles.toml), so you only list what you change. Valid `mode` values depend on the harness; see the [Herdr adapter](skills/deliver/adapters/herdr.md).

### Paseo

Roles use your Paseo agent profiles, not `delivery.toml`. Create four profiles in Paseo with the IDs `planner`, `implementer`, `reviewer` and `qa`, and set each one's provider, model and thinking level there. A missing profile stops the run at setup.

## Tests

```bash
python3 tests/test-deliver-runtime.py
python3 tests/test-deliver-orca-preflight.py
```

## License

[MIT](LICENSE) © 2026 flyingnobita
