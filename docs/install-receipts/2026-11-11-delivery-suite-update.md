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
| Codex | `~/.codex/skills` | no delivery skills installed | n/a | n/a |
| OpenCode | `~/.config/opencode/skills` | empty | n/a | n/a |
| Cursor | `~/.cursor/skills` | path absent | n/a | n/a |
| Grok | `~/.grok/skills` | empty | n/a | n/a |
| PromptScript | no skill directory on this host | path absent | n/a | n/a |
| Project scope | none | no `skills-lock.json` for this suite | n/a | n/a |

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

The install window was 19:34–19:36 +08. No delivery run was dispatching work: no
`deliver-runtime.py` or `deliver-orca-preflight.py` process was running and no delivery
`writer.lock` was held.

One suite skill invocation was nonetheless in flight. A Retro run for run
`1fed616647bc48c58e8aa91871865031` (`omarchy-notification-center`, Herdr) began at
19:32:21 and its record was last written at 19:42, so its window overlaps the update.
The record parses and carries the full `checks`, `gates`, `profiles`, `upstream` and
`candidates` sections, and the four skill trees were byte-identical to `a5cfdff`
afterwards, so the overlap did not corrupt the install or the run result. A copy of
that record sits in the recovery snapshot as `concurrent-retro-record.json`.

Three sibling issue workspaces (DLV-10, DLV-13, DLV-14) were also active against the
same installation. The update was therefore made reversible instead of asking them to
stop: content was snapshotted first, stale folders were replaced only after the new
install verified, and the prefixed names were kept as symlink aliases so a live
`flyingnobita-deliver*` reference still resolves.

Because that overlap means the "no affected delivery is active" condition was not
strictly met, it is an explicit deviation from the ticket, recorded here with the
evidence above rather than claimed as satisfied.

## Recovery information

Snapshot written before any change, at 19:30 +08:

```text
~/.local/state/deliver-skill-backups/dlv-9-20261111T113040Z/
  agents-skills-deliver-4.tgz   48 entries, the four v0.2.0 skill folders
  skill-lock.json               legacy ~/.agents/.skill-lock.json copy
  skill-prefix-state.json       ~/.agents/.skill-prefix-state.json copy
  state-lock-after-update.json  active CLI lock as written by this update
  concurrent-retro-record.json  the Retro record that overlapped the update
  SHA256SUMS
```

```text
c6afeb87664ccdc36d78369ff8b65ff35b705428c753823fd8a23b78a11c2ac2  agents-skills-deliver-4.tgz
f8613d1a428b9adc6e89090bc5373c240cb29a18be52a380f9db85f22a1f9ae2  concurrent-retro-record.json
d289f8b79f793bd74a93a357483eafe6a102d01cb6f1e59230a5643b494427a5  skill-lock.json
a7cccacdadbc42faf3300f7aec31f1820aa5e9f0801bac86b71f4ff7bbae23af  skill-prefix-state.json
5bbd47feac6780e3d30d10c673bceed5493e80cc9277a66c0316302c4e39c45f  state-lock-after-update.json
```

The active lock (`~/.local/state/skills/.skill-lock.json`) is rewritten in place by the
CLI, so its pre-update content was not captured; only the post-update copy is kept. To
reconstruct a v0.2.0 lock, install the tag: `npx skills add
flyingnobita/flyingnobita-deliver#v0.2.0 -g`.

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
4. `npx skills@latest check` no longer lists any of the four and reports no local
   changes for them. Its remaining 84 update notices are unrelated skills from other
   sources.

## Verification against `a5cfdff`

`git rev-parse origin/main` was `a5cfdff40e0dcdbfabdd0ba40c0fe3fe8ceada54` when the
install ran (19:34 +08), and the worktree was checked out at `a5cfdff` while the
comparisons below were made. Later commits on this branch carry this receipt only.

| Skill | Canonical path | Files | Tree SHA-256 | `diff -r` vs `skills/<name>` at `a5cfdff` |
| --- | --- | --- | --- | --- |
| deliver | `~/.agents/skills/deliver` | 28 | `aaf43474ab4e650b038e5d285275373a6ce805bfbe3bffa133e44b8ceb53608f` | identical |
| deliver-setup | `~/.agents/skills/deliver-setup` | 2 | `41bcb349fb554684a4b23565cc3a5a7f91bccf2fb4938c57d5a4a771c96c0169` | identical |
| deliver-review | `~/.agents/skills/deliver-review` | 1 | `20245dec9a0979e0c3754a2ae2a7b914f2e2a483ec199bbc18a52c0272ee50c7` | identical |
| deliver-retro | `~/.agents/skills/deliver-retro` | 8 | `6e37ba7707ddf1ccc11adb28e0e7ef36b9a64a3ed9424a27767ef051ff5d51bb` | identical |

Every tree SHA-256 is `find . -type f | sort | xargs sha256sum | sha256sum` over the
installed folder, which is how a later install is compared with this record.

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
| Claude Code (`~/.claude/skills`) | `a5cfdff` via symlink | four canonical links plus four prefixed links | links resolve, content identical | each skill appears under two names |
| Codex (`~/.codex/skills`) | no install | n/a | n/a | no delivery skill before or after |
| OpenCode (`~/.config/opencode/skills`) | no install | n/a | n/a | directory is empty |
| Cursor (`~/.cursor/skills`) | no install | n/a | n/a | path absent |
| Grok (`~/.grok/skills`) | no install | n/a | n/a | directory is empty |
| PromptScript | no install | n/a | refused a global install | no skill directory on this host |
| Remote host `thinkpad` | unknown | unreachable from this session | unverified | not updated |
| Remote host `xps` | unknown | unreachable from this session | unverified | not updated |
| Remote host `lifebook` | unknown | unreachable from this session | unverified | not updated |
| Remote host `rpi5` | unknown | unreachable from this session | unverified | not updated |
| Remote host `mbp-m4` | unknown | unreachable from this session | unverified | not updated |

## Gaps

1. The fleet's skill-prefix tooling reads `~/.agents/.skill-lock.json`, while Skills CLI
   1.8.1 writes `~/.local/state/skills/.skill-lock.json`. A prefix `strip`/`apply` cycle
   therefore does not see this install, so the prefixed names were restored as symlinks
   instead, and the superseded lock still carries prefixed keys for every skill.
2. The prefixed aliases keep the fleet naming working, which the README states the suite
   supports. They are untracked by the CLI, so `skills ls` and `skills check` see only
   the four canonical names.
3. PromptScript refused the global install; no PromptScript skill directory exists on
   this host, so nothing regressed there.
4. The remote-host installations in the table above were not inspected or updated.
5. `npx skills add` installs from the branch tip and the lock records no commit. The
   revision claim rests on the byte comparison above, taken while `origin/main` was
   `a5cfdff`.
6. A Retro run overlapped the install window (see above). Its record is complete, but
   the run cannot be called isolated from the update.
