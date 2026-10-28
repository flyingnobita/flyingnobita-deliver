# Review and repair

Shared by the delivery pipeline and standalone `flyingnobita-deliver-review`.
Keep the fixed-point SHA immutable through every iteration. The review result
is findings plus evidence; worker completion is not a clean-review verdict.

1. Start a read-only reviewer with `mattpocock-code-review`, the fixed point,
   approved brief/plan and source spec. Preserve its Standards and Spec axes.
   Ask it to save the findings outside disposable worktrees and identify the
   reviewed HEAD. The reviewer never edits code, commits or launches a fixer.
   On Orca, include this reference and the selected adapter in the reviewer
   brief. Before spawning Standards/Spec workers, the reviewer loads
   `orca-orchestration` and its full installed guide. Each axis receives a
   complete Task contract and the selected profile before its first launch.
   Compile each structured axis packet with `deliver-runtime orca-task` from
   [the Orca contract](orca-contract.md); preserve packet/spec and durable report
   evidence in the review artifact before releasing any child worker.
   Correct a live brief with a Dispatch follow-up; changing the brief or a
   timeout is not proof the worker exited. Apply the guide's lifecycle and
   output-preservation rules to nested workers too, and record every attempt
   and cleanup result, including failures, in the review artifact.
2. Read its evidence and classify findings:
   - **Must-fix:** a documented standard violation or missing, unrequested or
     wrong spec behavior.
   - **Mention:** judgement-call smells, unless a small repair is inside the plan.
   A finding changing scope returns to the user before edits.
3. Dispatch all must-fix findings to the implementer as a follow-up. Use TDD at
   the confirmed seams and `flyingnobita-clean-commit`. Reuse the agent when the
   adapter can prove its identity and settings; otherwise start a new one with
   the saved context. The orchestrator owns this dispatch, not the reviewer.
4. Independently rerun the full suite, linters and red check after repairs.
   Return to the reviewer for focused verification and a whole-diff Spec check
   from the original fixed point, catching regressions introduced by repairs.
   Repeat until no must-fix finding remains. Repeated inability to resolve the
   same finding is a blocker to report, not grounds to mark it clean.
5. Save the review file, iteration results, final HEAD, remaining Mention
   findings and independent commands/results in the run before cleanup.

Done when the last committed result has a green independent run, every
must-fix finding is verified resolved, and the reviewer examined that result.
For standalone review, red checks apply to new/changed repair tests against the
pre-repair commit; existing tests are not retroactively required to fail there.
