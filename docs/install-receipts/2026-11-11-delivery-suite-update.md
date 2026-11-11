# Delivery suite install update — 2026-11-11

Receipt for DLV-9 / issue #9. Machine: `north-omarchy` (Linux x64). Installed revision
baseline: `a5cfdff` (`docs: improve onboarding and align delivery skill conventions`).

## Scope and inventory before the update

Global scope only. Project-scope installs were not present for this suite, and the
agent directories other than Claude Code hold no delivery skills.

| Installation | Path | Form before | Revision before | Local changes |
| --- | --- | --- | --- | --- |
| Skills CLI global | `~/.agents/skills/flyingnobita-deliver` | prefixed folder, `name: flyingnobita-deliver` | `5495393` (v0.2.0) | none beyond the prefix rewrite |
| Skills CLI global | `~/.agents/skills/flyingnobita-deliver-setup` | prefixed folder | `5495393` | none beyond the prefix rewrite |
| Skills CLI global | `~/.agents/skills/flyingnobita-deliver-review` | prefixed folder | `5495393` | none beyond the prefix rewrite |
| Skills CLI global | `~/.agents/skills/flyingnobita-deliver-retro` | prefixed folder | `5495393` | none beyond the prefix rewrite |
| Claude Code view | `~/.claude/skills/flyingnobita-deliver{,-setup,-review,-retro}` | absolute symlinks to the rows above | inherited | n/a |
| Codex, OpenCode, Cursor, Grok, project scope | `~/.codex/skills`, `~/.config/opencode/skills`, `~/.cursor/skills`, `~/.grok/skills` | no delivery skills installed | n/a | n/a |

Lock entries before the update: `~/.local/state/skills/.skill-lock.json` keys
`deliver`, `deliver-setup`, `deliver-review`, `deliver-retro`, `updatedAt`
`2026-11-11T11:26:39Z`. The stale `~/.agents/.skill-lock.json` still holds the
prefixed keys (see Gaps).

Revision evidence: prefix-normalized byte comparison against `git archive 5495393`
matched all four skill folders exactly, so the installed content was v0.2.0, missing
`references/environment.md` and `references/retro-LICENSE.txt`.

Unavailable installations: delivery suite installations on the remote Herdr hosts
(`thinkpad`, `xps`, `lifebook`, `rpi5`, `mbp-m4`) are not reachable from this session
and were not touched.

## Live-state check at update time

No delivery run was active on this host at 19:34 +08:

- no `deliver-runtime.py` or `deliver-orca-preflight.py` process;
- no file under `~/.local/state/flyingnobita-deliver` written in the preceding 6 hours;
- no recent `writer.lock`;
- Herdr workspaces: `w1B` idle, `w1C` (DLV-14) idle, `w1D` (DLV-9, this session)
  working, `w1E` (DLV-10) working, `w1F` (DLV-13) working. These are issue-implementing
  agents that share the installation; none is a delivery run.

The shared installation was nonetheless in use, so the update was made reversible
instead of asking those agents to stop: content was snapshot first, stale folders were
replaced only after the new install verified, and the prefixed names were kept as
symlink aliases so a live agent's `flyingnobita-deliver*` references still resolve.

## Recovery information

Snapshot written before any change, at 19:30 +08:

```text
~/.local/state/deliver-skill-backups/dlv-9-20261111T113040Z/
  agents-skills-deliver-4.tgz   48 entries, the four v0.2.0 skill folders
  skill-lock.json               legacy ~/.agents/.skill-lock.json copy
  skill-prefix-state.json       ~/.agents/.skill-prefix-state.json copy
  SHA256SUMS
```

```text
c6afeb87664ccdc36d78369ff8b65ff35b705428c753823fd8a23b78a11c2ac2  agents-skills-deliver-4.tgz
d289f8b79f793bd74a93a357483eafe6a102d01cb6f1e59230a5643b494427a5  skill-lock.json
a7cccacdadbc42faf3300f7aec31f1820aa5e9f0801bac86b71f4ff7bbae23af  skill-prefix-state.json
```

Restore the previous content:

```bash
rm -f ~/.agents/skills/flyingnobita-deliver{,-setup,-review,-retro}
rm -rf ~/.agents/skills/deliver{,-setup,-review,-retro}
tar -xzf ~/.local/state/deliver-skill-backups/dlv-9-20261111T113040Z/agents-skills-deliver-4.tgz \
  -C ~/.agents/skills
```

## Update procedure and results

1. `npx skills@latest check` reported `deliver`, `deliver-retro`, `deliver-review` and
   `deliver-setup` as having updates.
2. `npx skills@latest add flyingnobita/flyingnobita-deliver -g -y` installed the four
   published skills to `~/.agents/skills/deliver{,-setup,-review,-retro}` and symlinked
   them into `~/.claude/skills`. PromptScript, one of the detected agent targets,
   rejected a global install (`PromptScript does not support global skill installation`);
   the canonical install and the Claude Code link succeeded.
3. Removed the four stale prefixed folders, then recreated each prefixed name as a
   symlink to its canonical folder.
4. `npx skills@latest check` no longer lists any of the four, and lists 84 unrelated
   skills still behind their own sources. No `has local changes` report for the suite.

## Verification against `a5cfdff`

`git rev-parse HEAD` = `git rev-parse origin/main` = `a5cfdff40e0dcdbfabdd0ba40c0fe3fe8ceada54`
in this worktree, so the install source tip equals the record below.

| Skill | Canonical path | Files | Tree SHA-256 | `diff -r` vs `skills/<name>` at `a5cfdff` |
| --- | --- | --- | --- | --- |
| deliver | `~/.agents/skills/deliver` | 28 | `aaf43474ab4e650b038e5d285275373a6ce805bfbe3bffa133e44b8ceb53608f` | identical |
| deliver-setup | `~/.agents/skills/deliver-setup` | 2 | `41bcb349fb554684a4b23565cc3a5a7f91bccf2fb4938c57d5a4a771c96c0169` | identical |
| deliver-review | `~/.agents/skills/deliver-review` | 1 | `20245dec9a0979e0c3754a2ae2a7b914f2e2a483ec199bbc18a52c0272ee50c7` | identical |
| deliver-retro | `~/.agents/skills/deliver-retro` | 8 | `6e37ba7707ddf1ccc11adb28e0e7ef36b9a64a3ed9424a27767ef051ff5d51bb` | identical |

Every tree SHA-256 is `find . -type f | sort | xargs sha256sum | sha256sum` over the
installed folder, so the same command on a future install identifies the revision.

Required artifacts for this revision:

- `~/.agents/skills/deliver-retro/references/environment.md` (66 lines), the local
  environment-review procedure;
- `~/.agents/skills/deliver-retro/references/retro-LICENSE.txt`, `MIT License`,
  `Copyright (c) 2026 Matt Pocock` (1068 bytes).

Skill discovery: `npx skills@latest ls -g` lists the four canonical folders with source
`flyingnobita/flyingnobita-deliver`, and Claude Code sees them through
`~/.claude/skills/deliver{,-setup,-review,-retro}`. The prefixed aliases resolve to the
same content (`diff -r` clean through each `flyingnobita-*` path).

Lock state after the update, `~/.local/state/skills/.skill-lock.json`:

| Key | `skillPath` | `skillFolderHash` | `updatedAt` |
| --- | --- | --- | --- |
| deliver | skills/deliver/SKILL.md | e0b4441b37b7596258cfd9dc2f61f453a539082e | 2026-11-11T11:34:58Z |
| deliver-setup | skills/deliver-setup/SKILL.md | 7bf7f6ce8dfacc95cc18e5186e043de061829cdd | 2026-11-11T11:34:58Z |
| deliver-review | skills/deliver-review/SKILL.md | de62040de68679c5dc1bb50c229702a4096ab9ba | 2026-11-11T11:34:58Z |
| deliver-retro | skills/deliver-retro/SKILL.md | 99cf9dcf82f60b2f8b505ac24604b32a6bc3b970 | 2026-11-11T11:34:58Z |

## Per-installation result

| Installation | Revision installed | Discovery | Verification | Remaining gap |
| --- | --- | --- | --- | --- |
| Skills CLI global (`~/.agents/skills`) | `a5cfdff` | `skills ls -g`, four canonical names | byte-identical to `a5cfdff`, required artifacts present | prefixed aliases are untracked by the CLI |
| Claude Code (`~/.claude/skills`) | `a5cfdff` via symlink | four canonical links plus four prefixed links | links resolve, content identical | duplicate names list twice |
| Codex, OpenCode, Cursor, Grok | not installed | n/a | n/a | out of scope, unchanged |
| Remote Herdr hosts | unknown | unreachable | unverified | not updated from this session |

## Gaps

1. Prefix tooling reads the old lock path. `~/dotfiles/scripts/common/npx-skills-prefix`
   uses `~/.agents/.skill-lock.json`, while Skills CLI 1.8.1 writes
   `~/.local/state/skills/.skill-lock.json`. A prefix `strip`/`apply` cycle therefore
   cannot see this install, and the fleet's prefixed names would not be recreated by it.
   The current prefixed aliases are hand-made symlinks, and the stale legacy lock keeps
   prefixed keys for all skills.
2. The prefixed aliases are a compatibility measure for agents that started before the
   update and for the fleet's prefixed naming. Remove them once no session depends on the
   prefixed names: `rm ~/.agents/skills/flyingnobita-deliver{,-setup,-review,-retro}`
   together with `~/.claude/skills/flyingnobita-deliver{,-setup,-review,-retro}`.
3. PromptScript rejections leave one agent target without a global install. No delivery
   skill was installed there before either, so nothing regressed.
4. Remote-host installations were not inspected or updated.
5. `npx skills add` runs from the branch tip, and the lock records no commit. The
   revision claim rests on the byte comparison above, taken while `origin/main` was
   `a5cfdff`.
