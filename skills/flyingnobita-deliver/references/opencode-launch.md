# OpenCode full-TUI launch

Use this branch when a resolved Herdr profile selects `opencode`.
OpenCode V2 Mini/headless clients do not run Herdr's pane-local reporter;
[Herdr v0.9.5 documents this limitation](https://github.com/herdrdev/herdr/blob/v0.9.5/docs/next/website/src/content/docs/integrations.mdx#L194-L204).
The full TUI has no model/variant CLI flags. Select them on a fresh native
session before launching the TUI with `--session`.

1. Validate profiles normally. For OpenCode, `profiles` returns `argv: null`
   and `session_request: {model: {providerID, id, variant}}`. Null means startup
   is blocked pending a native session; it never means launch without arguments.
   Keep `mode = "default"`; no automatic-approval flag is added. Check that the
   requested model/variant is available in the installed native model catalog.
2. After creating and registering the owned worker worktree/attempt, append
   `location: {directory: <absolute worktree path>}` and an identifying title to
   the returned session request. Record `operation-intent` with operation
   `opencode-session-create` and the exact request/directory before mutation.
   Use `opencode api session.create --data <serialized JSON>` through separate
   argv elements. It creates metadata only; include no task prompt, permission
   overrides or agent changes. Save its native response with `operation-result`.
   An uncertain creation is inspected and reconciled, never blindly repeated.
3. Read that exact native session again with
   `opencode api session.get --param sessionID=<returned ID>`. Retain the receipt.
   Call `profiles` again with the same role inputs and an `opencode_sessions`
   binding for the selected role:

   ```json
   {
     "opencode_sessions": {
       "implementer": {
         "directory": "/absolute/owned-worktree",
         "session": {
           "id": "ses_NATIVE_RETURNED_ID",
           "model": {"providerID": "deepseek", "id": "deepseek-flash", "variant": "high"},
           "location": {"directory": "/absolute/owned-worktree"}
         }
       }
     }
   }
   ```

   `session` is the actual response's `data` object, not a fabricated replacement.
   The helper validates exact model/variant, expected directory and native ID,
   then returns `argv: ["--session", "<native ID>"]`. A mismatch stops startup.
   Binding validates supplied evidence; it does not query OpenCode itself or
   establish model availability. Preserve the native receipt and startup proof.
4. Journal `agent-start`, then start `--kind opencode` with the returned argv.
   This launches the full TUI, retaining the host's native approval policy.
   Check its effective model/variant and the Herdr-reported session against the
   saved native ID before `profile-bind` and the normal strict runtime `prompt`.
   Require a current integration and the V2 TUI registration in `cli.json`.
   Missing reports remain a blocker; neither Mini nor weaker permissions is a
   fallback. Observe working and completion after the saved baseline.
5. Revalidate the session, task report, independent checks and worktree state
   before verification and owned cleanup. Retain native session/report evidence.

Bounded acceptance observed native identity, working and done status with
DeepSeek Flash/high/default, zero tools and no edits under full TUI.
It establishes this launch path, not a complete delivery cycle for every role,
provider or model. Do not claim platform or live compatibility beyond checked evidence.
