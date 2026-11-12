# Deliver skills

Turn a GitHub issue into reviewed code with a team of coding agents. Choose a different model for planning, implementation, and review.

Runs [Matt Pocock's skills](https://github.com/mattpocock/skills) (`grilling`, `tdd`, `code-review`, `pr` and the rest) across [Herdr](https://herdr.dev), [Paseo](https://paseo.sh) and [Orca](https://www.onorca.dev). Each role can run on its own harness (Claude Code, Codex and so on), model and effort level. The orchestrator re-checks every agent's work before it ships.

## Already using Matt Pocock's skills?

Then you no longer need a separate prompt for each step: grilling, writing the spec, implementing, reviewing and writing the PR. Run `deliver` once and it does every step, handing each one to a role on the harness and model you chose. You still answer the grilling questions yourself.

Here is where each step you run today goes:

| You run today                                  | In `deliver`                                                                                                                                                                             |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/grill-me` (loads `grilling`)                 | The **orchestrator**, your own session, loads `grilling` and `domain-modeling`                                                                                                           |
| `/to-spec`, `/to-tickets`                      | The **planner** writes the plan and splits it into tickets itself. It loads `diagnosing-bugs` for a bug with an unknown cause, and may load `research`, `codebase-design` or `prototype` |
| `/implement` (loads `tdd`, then `code-review`) | The **implementer** loads `tdd`, then the **reviewer** loads `code-review`                                                                                                               |
| `pr`                                           | The **orchestrator** runs `pr` when the run ships as a pull request                                                                                                                      |

You can still hand `deliver` a spec or tickets you wrote with `/to-spec` or `/to-tickets`.

On top of those skills, `deliver` adds:

- **A model per role.** Each role gets its own harness, model and effort. For example, review with a different vendor's model from the one that wrote the code.
- **Lower costs.** Give the **implementer** a cheaper model and keep the expensive ones for the **planner** and the **orchestrator**. The implementer runs longest: it writes the code, runs the tests and fixes what fails. The orchestrator reruns the tests itself, so it catches a weaker model's mistakes before they ship.
- **Parallel builds.** Independent parts of a change become tickets, each with its own worktree and implementer, up to `max_workers` at once.
- **Your choice of host.** Each agent is a visible session in [Herdr](https://herdr.dev), [Paseo](https://paseo.sh) or [Orca](https://www.onorca.dev).
- **Checks between handoffs.** The orchestrator reruns the tests and linters itself before it accepts an agent's report.

Your installed skills stay as they are. [dependencies.md](skills/deliver/references/dependencies.md) lists what each role loads.

## Quick start

Choose your host below.

<details>
<summary><strong>Herdr</strong></summary>

This path uses Herdr on Linux with Codex for all roles. Start with one model your account can access; you can choose different models later.

You need [Herdr](https://github.com/herdrdev/herdr), an installed and authenticated Codex CLI, Node.js/npm for `npx`, and the [shared prerequisites](#prerequisites). Use a small GitHub repository you own, with a clean working tree and a remote default branch.

1. Install the skills in a terminal:

   ```bash
   npx skills add flyingnobita/flyingnobita-deliver -g
   npx skills add mattpocock/skills -g
   npx skills add herdrdev/herdr --skill herdr -g
   ```

2. Open your repository in Herdr and start a fresh Codex session so it loads the installed skills. Codex picks a skill from your request rather than a slash command, so name the skill and the settings:

   ```text
   Run the deliver-setup skill: use Codex for planner, implementer, reviewer and QA, with one model available to my account. Validate all four profiles. Set max_workers = 1 and landing = "leave".
   ```

   Review the proposed settings and approve them. Setup checks prerequisites, identifies any integration fixes, validates the profiles with no-edit smoke tasks, and records the configuration in `docs/agents/delivery.toml`. Resolve any reported blocker before continuing.

   If setup reports the Herdr Codex integration missing, approve `herdr integration install codex` and restart the Codex session: Herdr reads a session's identity at startup, so setup cannot match the running session until it restarts. Without a restart, run `/status` in that session and paste the session ID it reports.

3. Run the [first-delivery example](examples/first-delivery.md), or give the agent one small task:

   ```text
   deliver <describe one small change>; keep landing = "leave"
   ```

4. Answer the brief questions and approve the plan. At completion, inspect the reported branch and test results. With `landing = "leave"`, the run ends with a committed local branch, without pushing, opening a PR or merging.

</details>

<details>
<summary><strong>Orca</strong></summary>

You need [Orca](https://www.onorca.dev), an installed and authenticated Codex CLI, Node.js/npm for `npx`, and the [shared prerequisites](#prerequisites). Use a small GitHub repository you own, with a clean working tree and a remote default branch.

1. Install the skills in a terminal:

   ```bash
   npx skills add flyingnobita/flyingnobita-deliver -g
   npx skills add mattpocock/skills -g
   ```

2. Open your repository in Orca and start a fresh Codex session so it loads the installed skills. Codex picks a skill from your request rather than a slash command, so name the skill and the settings:

   ```text
   Run the deliver-setup skill: use Codex for planner, implementer, reviewer and QA, with one model available to my account. Validate all four profiles. Set max_workers = 1 and landing = "leave".
   ```

   Review the proposed settings and approve them. Setup checks Orca's CLI and bundled orchestration guide, validates the profiles with no-edit smoke tasks, and records the configuration in `docs/agents/delivery.toml`. Resolve any reported blocker before continuing. A separately installed orchestration skill is not required when Orca's bundled guide is available.

3. Give the agent one small task:

   ```text
   deliver <describe one small change>; keep landing = "leave"
   ```

4. Answer the brief questions and approve the plan. At completion, inspect the reported branch and test results. The run does not push, open a PR or merge with `landing = "leave"`.

</details>

<details>
<summary><strong>Paseo</strong></summary>

You need [Paseo](https://github.com/getpaseo/paseo) with its daemon running, an authenticated agent provider, Node.js/npm for `npx`, and the [shared prerequisites](#prerequisites). Use a small GitHub repository you own, with a clean working tree and a remote default branch.

1. Install the skills on the machine where your Paseo agents run, where their harness can discover them:

   ```bash
   npx skills add flyingnobita/flyingnobita-deliver -g
   npx skills add mattpocock/skills -g
   ```

2. In Paseo, create four agent profiles with the IDs `planner`, `implementer`, `reviewer` and `qa`. Choose a provider and model your account can access for each. Configure the planner in plan mode. These profiles live in Paseo, rather than in `delivery.toml`.

3. Open your repository in Paseo and start a fresh Claude Code or Codex session with access to the Paseo MCP tools and installed skills. In Claude Code, send:

   ```text
   /deliver-setup
   ```

   Codex has no `/deliver-setup` command, so name the `deliver-setup` skill in your request instead.

   Ask setup: "Use my existing planner, implementer, reviewer and qa profiles. Validate all four profiles. Set max_workers = 1 and landing = \"leave\"."

   Review the proposed settings and approve them. Setup checks the caller's Paseo connection and profile availability, validates the profiles with no-edit smoke tasks, and records shared delivery settings in `docs/agents/delivery.toml`. Approve the session's requests to create Paseo workspaces and agents when your harness asks: a denied request leaves that profile unvalidated and setup stops there. Resolve any other reported blocker before continuing.

4. Give the agent one small task:

   ```text
   deliver <describe one small change>; keep landing = "leave"
   ```

   Answer the brief questions and approve the plan. At completion, inspect the reported branch and test results. The run does not push, open a PR or merge with `landing = "leave"`.

</details>

## Harness

The following harnesses are supported through Herdr, Orca and Paseo:

- Claude Code
- Codex
- Antigravity
- Pi
- omp
- OpenCode

Other harnesses may require additional integration work.

## Roles

- **Orchestrator:** your own session, in Claude Code or Codex (Orca also accepts Antigravity). Grills you on the brief, starts the other roles, checks their evidence and ships.
- **Planner:** reads the code and the agreed brief, then splits the work into ordered slices. Read-only.
- **Implementer:** builds each slice test-first and commits.
- **Reviewer:** reviews the branch against the repo's standards and the spec.
- **QA:** tests the change in a live environment, when you ask for it.

Each role except the orchestrator gets its own profile. For example:

| Role        | Harness  | Model                             | Effort |
| ----------- | -------- | --------------------------------- | ------ |
| Planner     | `claude` | `claude-opus-5-5`                 | `high` |
| Implementer | `pi`     | `opencode-go/deepseek-v4.1-flash` | `high` |
| Reviewer    | `codex`  | `gpt-6.1-sol`                     | `low`  |
| QA          | `codex`  | `gpt-6.1-sol`                     | `low`  |

## Skills

| Skill                                                    | What it does                                                                | How to run it                                      |
| -------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| [`deliver`](skills/deliver/SKILL.md)                     | Runs a full delivery                                                        | `deliver <input>` (issue URL, `#N`, spec or brief) |
| [`deliver-implement`](skills/deliver-implement/SKILL.md) | Implements agreed tickets in parallel workers and lands each on your branch | `deliver-implement 1,2,3`                          |
| [`deliver-setup`](skills/deliver-setup/SKILL.md)         | Checks prerequisites, configures role profiles, validates hosts             | `/deliver-setup`                                   |
| [`deliver-review`](skills/deliver-review/SKILL.md)       | Reviews and repairs an existing branch against standards and spec           | `/deliver-review`                                  |
| [`deliver-retro`](skills/deliver-retro/SKILL.md)         | Looks back over past runs and proposes fixes to the skills and profiles     | `/deliver-retro`                                   |

The `flyingnobita-` prefix is a fleet convention, not part of these names. Fleet installs still see `flyingnobita-deliver`, `flyingnobita-deliver-setup` and so on, and the suite resolves both forms.

## Install

With the [Skills CLI](https://github.com/vercel-labs/skills) (`skills`, or `npx skills`):

```bash
skills add flyingnobita/flyingnobita-deliver -g   # global
skills add flyingnobita/flyingnobita-deliver      # current project only
```

This installs from `main`. To pin a release, add the tag:

```bash
skills add flyingnobita/flyingnobita-deliver#v0.2.0 -g
```

To update, pass the installed skill names, not the repo slug:

```bash
skills update deliver deliver-implement deliver-setup deliver-review deliver-retro -g
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

Use `[hosts.herdr.roles.<role>]` tables. Each takes `harness`, `model`, `effort` and `mode`:

```toml
[hosts.herdr.roles.planner]
harness = "pi"
model = "opencode-go/kimi-k3.1-pro"
effort = "high"
mode = "default"

[hosts.herdr.roles.qa]
harness = "codex"
model = "gpt-6.1-sol"
effort = "medium"
mode = "auto"
```

Fields you set are merged over the [defaults](skills/deliver/references/herdr-profiles.toml), so you only list what you change. A file that still has only the old top-level `[planner]`, `[implementer]`, `[reviewer]` and `[qa]` tables is read the same way, with a warning; `deliver-setup` (or `flyingnobita-deliver-setup`) moves them under `[hosts.herdr.roles.*]`. Valid `mode` values depend on the harness; see the [Herdr adapter](skills/deliver/adapters/herdr.md).

### Paseo

Roles use your Paseo agent profiles, not `delivery.toml`. Create four profiles in Paseo with the IDs `planner`, `implementer`, `reviewer` and `qa`, and set each one's provider, model and thinking level there. A missing profile stops the run at setup.

## Tests

```bash
python3 tests/test-deliver-runtime.py
python3 tests/test-deliver-orca-preflight.py
```

Both suites need Python 3.11+, and the runtime suite also needs `git` on `PATH`. [GitHub Actions](.github/workflows/tests.yml) runs them on Python 3.11 for every pull request and every push to `main`.

## License

[MIT](LICENSE) © 2026 flyingnobita
