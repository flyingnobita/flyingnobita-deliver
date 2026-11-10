# Outstanding work in the chosen tracker

Use this to prepare the final offer at delivery wrap-up or after a retrospective.
Save only the creates/updates selected by the user. The tracker is the user's
central work list; run reports and the retro ledger retain evidence and history,
linked to that list.

## Resolve the destination

Use the tracker explicitly chosen for this project/run. Read the project's
`docs/agents/issue-tracker.md` for its operations and the `Tracker default` under
`## Delivery` in `AGENTS.md` where present. Preserve the run's explicit choice
over a general default. A GitHub remote alone is not a tracker selection.

If the choice is missing or conflicting, prepare the concrete outstanding list
and ask once where to store it. Offer the project's established tracker first;
otherwise offer GitHub/GitLab issues or local Markdown as appropriate. Suggest
`mattpocock-setup-matt-pocock-skills` for a persistent project choice. Do not
require setup merely to record this run's items. Respect an explicit `none` or
declined write: retain the list in the existing private run/retro artifact and
report that it was not centralized. Never create a parallel tracker silently.

## Reconcile and save

1. Collect unresolved actions from the brief, implementation reports, review
   mentions, QA, publication, deployment, cleanup and explicit deferred scope.
   Remove items now completed by inspected evidence. Separate actionable TODOs,
   optional proposals, verification gaps and accepted product limitations. A
   limitation with no proposed action stays linked reference context rather
   than an invented task. Log an agreed investigation when its resolution is
   unknown; preserve unknown ownership or timing rather than guessing.
2. Search the chosen tracker for matching work before creating anything. Match
   the project, intended outcome and existing ticket or retro candidate ID.
   Propose an update/reopen when appropriate; preserve its identity and
   history. Apply it only if selected in the final offer. Use the tracker's
   grouping, labels and dependencies.
   On repeated wrap-ups, reuse the same entries. If several systems are required
   by project rules, identify one canonical task and use links in the others.
3. Each entry names the outcome, reason it remains open, status (for example
   proposed, deferred, blocked or ready), next trigger/dependency, known owner
   or `unassigned`, completion evidence and relevant source references. Include
   the delivery run/task or retro candidate ID for traceability. Do not invent
   a deadline, implementation approval or an external dependency. Proposed
   improvements remain proposals until selected; use configured triage labels.
4. Before any wrap-up tracker write, present the destination and concrete
   creates/updates and ask for all, selected items, or none. Both Deliver and
   Retro require this selection; tracker configuration, delivery approval and
   silence do not grant it. Retain pending, declined and unselected items in
   the private run/retro artifact. Reuse an explicit selection already made
   for this exact offer instead of asking again. Save only the selected items
   through the tracker's documented operations, within any upstream posting
   scope selected at intake. Public tracker text
   uses sanitized facts and stable public links, never private paths, raw logs
   or credential contents. Cross-project tooling work belongs in its owning
   project's tracker, with a pointer from this project's central list.
5. Read back every saved entry to verify its body, status and references. For
   local Markdown, check links/format and record whether files are tracked,
   ignored or committed under that project's convention. If tracker updates
   require a commit, follow repository commit rules (or a configured custom commit skill)
   and relevant checks; publication still follows the user's existing authorization. Do not modify
   product files or invalidate a shipped artifact to store private run notes.

The final report links the tracker index or saved entries and distinguishes
saved, already tracked and unsaved items. On a write failure, retain the prepared
items in the existing private artifact, name the failed operation and report
the unsaved count. Never claim all items were stored from a successful command
alone. Saving TODOs grants no authority to implement, deploy or publish them.
