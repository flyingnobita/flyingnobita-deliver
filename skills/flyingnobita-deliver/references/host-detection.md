# Select the current host

Run this at entry and resume, before creating resources. Installation, tool
availability, UI focus and matching directories do not establish membership.
Inspect only named identity fields; retain no credentials.

1. Herdr context absent: `HERDR_ENV` and inherited pane/session fields are all
   absent. If any marker exists, require `HERDR_ENV=1`, load `herdr`, and resolve
   `herdr pane current --current`. Require a recognized executing harness and
   compare `agent_session.value` with the executing session's ID when available.
   For Codex, read `CODEX_THREAD_ID` in the executing tool process; for Claude,
   read `CLAUDE_CODE_SESSION_ID`. Compare that value with the live report; a
   recognized pane alone is insufficient. A completed exec or parent session
   is not the executing child.
   Record the socket/server session identity, returned pane and harness session.
   Use caller lookup even if the inherited pane ID differs after a move.
   Connection errors, mismatched harness IDs or unresolved nested identities are
   broken context, not absence. If a trustworthy executing identity cannot be
   established, stop rather than accepting a plausible pane.
2. Paseo context absent: both `PASEO_AGENT_ID` and `PASEO_AGENT_CWD` are absent
   and no caller-bound connection identifies this execution. Otherwise use the
   existing caller-bound MCP connection to inspect its owning daemon's live
   agent/session. Require the caller identity to match `PASEO_AGENT_ID` and the
   actual running harness session. A stored inactive record is insufficient.
   Missing tools, connection failures and unresolved nesting are broken context.
   Never launch the desktop `paseo` binary to probe identity.
3. Orca context absent: no Orca caller/session/worktree markers or live
   caller-bound connection identify this execution. If any exists, resolve the Orca
   executable (`ORCA_CLI_COMMAND` if set; `orca-dev` in a dev context; `orca-ide` on
   Linux outside an Orca-managed terminal; otherwise `orca`) and load the full
   version-matched orchestration guide with `ORCA skills get orchestration --full`
   (fetching any omitted references with `ORCA skills get orchestration --reference references/<file>.md`
   if output is truncated), or via `orca-orchestration` if installed.
   Read [the Orca contract](orca-contract.md), then run
   `deliver-orca-preflight` with the canonical repo on stdin. Use its explicit
   classification, host binding and evidence; stop on a broken result. The
   executable distinguishes structured chats from terminal agents and verifies
   the executing harness's own binding. A workspace marker or matching cwd
   alone is insufficient. Preserve stale or ambiguous context for the installed
   guide's recovery; never borrow a handle or inject identity fields.
4. Feed all three classifications to `deliver-runtime select-host` as JSON on stdin:
   `{"herdr":"absent","paseo":"absent","orca":"confirmed"}`. Every host must
   be classified explicitly. Exactly one confirmed selects that host. Multiple
   confirmed hosts require the user's explicit `choice` among confirmed hosts;
   none stops. Any broken/ambiguous classification stops even if another host
   is confirmed. The helper validates the matrix; the orchestrator obtains real
   caller evidence. Updated callers must include Orca even on Paseo/Herdr.
5. Save the evidence and selected host in the run. On resume repeat the live
   checks and compare the server/session and repo binding. A replacement
   orchestrator may have a new pane or session: retain the previous binding and
   append independently verified replacement evidence before continuing (a new
   session also needs the user's confirmation; see the adapter's `checkpoint`).
   A host change requires a new run, not a silent adapter switch.

Marker sets can be inherited by nested agents. If their live records cannot
disambiguate the executing harness, report the failed checks and stop.

The legacy `select` command remains compatible with deployed two-host callers;
new and migrated skills must use `select-host` to require all three checks.
