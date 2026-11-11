# Environment review

Adapted from Matt Pocock's [retro skill at commit 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/retro/SKILL.md).
Copyright (c) 2026 Matt Pocock. Distributed under the [MIT license](retro-LICENSE.txt).
This local procedure reviews one agent's environment. Deliver Retro owns the
coordination checks, combined presentation and implementation approval.

## 1. Read the evidence

Call the Skill tool with `writing-for-agents` (or `mattpocock-writing-for-agents`)
for the writing guidance. If unavailable, use the project's existing document
conventions and name the missing style guide in the report.

Read the primary sources for the requested session, defaulting to the current
orchestrator's session. Follow [evidence](evidence.md) for transcripts, run
records and branch history. Inspect existing project instructions, documentation,
coding standards, check commands, hooks and CI before proposing additions.
Read sources without changing them; retain sanitized pointers rather than raw
transcript excerpts or secrets.

Done when the relevant sources and existing checks are identified, with any
missing evidence named.

## 2. Review the environment

Check each category against the session evidence:

- **Navigation:** identify time lost finding files or hidden dependencies.
  Propose a focused navigation pointer where it would have prevented the search.
- **Automated checks:** identify mistakes that a linter, type check, test or
  filesystem check could catch. Inspect existing commands and their wiring
  first; an existing but unwired or broken check is the finding. A repo with
  neither a pre-commit gate nor CI running its checks is also a candidate.
- **Coding standards:** distinguish mechanical violations from judgement calls.
  Prefer the cheapest suitable deterministic check for mechanical rules; reserve
  `CODING_STANDARDS.md` for decisions a check cannot make. The reviewer owns
  standards enforcement so implementation instructions stay focused.
- **Global AGENTS.md:** inspect large project or global steering files for rules
  better enforced automatically or reached through a coding-standards pointer.
  Treat both `AGENTS.md` and `CLAUDE.md` as scarce always-loaded context.
- **Tool economy:** identify expensive calls, oversized responses and repeated
  lookups that a smaller query or existing tool could avoid.
- **No-ops:** identify steering instructions that add context without changing
  useful behavior. Cite evidence for removal rather than assuming a rule is idle.
- **Information access:** identify missing information that caused an error or
  unproductive search, such as inaccessible logs or a missing read-only source.

Prefer existing docs and navigation pointers over duplicate instructions.
Keep coordination and role-split findings under the matching C/R check in
[checks](checks.md); report an overlapping finding once.

Done when every category is marked with a finding, clean with evidence, or
unavailable with its missing evidence.

## 3. Prepare improvement candidates

For each finding, record its category as the check ID, sanitized evidence,
proposed smallest fix, owning file and observable measure of success. These
are proposals; they grant no authority to edit files or run external writes.

Return candidates and clean/unavailable category results to Deliver Retro.
Hold presentation for its step 7, where candidates receive the shared severity,
origin and recurrence treatment and join the multi-agent findings in one report.

Done when candidates and coverage results are ready for the combined review,
without a separate user-facing report.
