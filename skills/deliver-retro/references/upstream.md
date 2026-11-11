# Upstream retro comparison

The local [environment review](environment.md) is adapted from Matt Pocock's
`retro`. Its source revision and license are recorded there. Upstream `retro`
is user-invoked; Deliver Retro runs its own local procedure, not that skill.
Installing upstream `retro` is optional.

## Compare when an upstream copy is available

During Deliver Retro step 1, read the installed `retro` or `mattpocock-retro`
`SKILL.md` as comparison data only. Compare its environment categories, evidence
requirements, writing guidance and recommendations with `environment.md`.
An unavailable copy is a comparison gap, not a blocker to the local review.

Record the revision compared: a Skills CLI install has no git revision, so use
the copy's `skillFolderHash` from the Skills CLI lock
(`~/.local/state/skills/.skill-lock.json`; older installs keep a copy at
`~/.agents/.skill-lock.json`), together with its `updatedAt` date. The hash is
the git tree hash of the skill directory, so it matches
`git rev-parse <commit>:skills/<skill>`. A git checkout instead uses
`git -C <install> rev-parse HEAD`. A plain copy with neither is recorded by path
and comparison date.

Identify useful additions, removed or renamed categories, and changed guidance.
Use category meaning rather than upstream step numbers; its presentation order
does not control Deliver Retro. Hold all findings for the combined report.

Keep findings about coordination or role split under [checks](checks.md), not
duplicated in the environment categories. A new upstream category may add an
environment concern without replacing a C/R check.

Done when useful differences or an unavailable comparison are recorded.

## Propose an update

A difference is a maintenance candidate, not permission to change this skill
or the upstream installation. Name the upstream source and proposed local
change in the combined report. Apply only an approved update to `environment.md`,
retaining attribution and the license; update its source revision when the
adaptation is refreshed against that revision. Preserve Deliver's combined
presentation, read-only review and separate implementation-approval rules.
