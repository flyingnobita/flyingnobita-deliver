# Pipeline

This follows Matt Pocock's implement workflow (`mattpocock-implement`, `mattpocock-implement-spec`) with the user's profiles: one implementer drives `mattpocock-tdd` at the seams approved at the plan stop, commits, and `mattpocock-code-review` reviews. Your own checks sit on top of it.

Roles and their profiles come from the adapter. Every role brief:

- points to the brief, the approved plan, and its seams rather than restating them;
- asks for a numbered report: what changed, each command run and its result.
- names owned and frozen shared files, their current and deferred owners, and the
  extension hooks the ticket can use;
- distinguishes plan-settled limitations from outstanding acceptance checks;
- names fixture/source-mutating commands. Worker and independent checks use
  separate disposable copies, or an explicit serial handoff in one worktree;
- names the checks to run: the plan's required test list by name, plus every
  test that references a changed file. Your independent run uses the same set,
  never a narrower hand-picked one;
- carries the pinned test environment recorded at the baseline (variables and
  tool paths, nothing inherited from your shell) and the known host hazards,
  such as tools that hang under a fake home. After each test command the worker
  checks for processes it left behind.

Done when the worker can identify its shared interfaces, escalation boundary
and verification commands from the packet's focused pointers without exploring
the entire plan again. Answer plan-settled ownership questions in the packet.

For native `report`/`verify` implementer tasks, include the structured
[test evidence contract](test-evidence.md) in the brief. Record exact test
snapshots and independent before/after receipts; classify guards, bootstrap
checks and no-test changes explicitly.

Verify each gate yourself in the work's workspace. A role's report tells you where to look; your own run is the evidence.

## Single unit

### Build

Start the implementer role. Its brief:

- load `tdd` (or `mattpocock-tdd`) and work in vertical red-green slices, testing only at the seams listed in the approved plan; those seams are already confirmed with the user, so it starts without asking;
- run single test files as it goes, then the full suite, linters and the repo's pre-commit hooks at the end;
- produce each behavioural group's red on the base subject commit by running only that named test there, with a filtered command whose shape targets one test, such as `python3 -m unittest path.to.TestCase.test_name`, `pytest path::test_name` or `node --test --test-name-pattern '<name>'`; a run of the whole test file counts only when it executed exactly that one test. Record that command with the group and report the group through the [test evidence contract](test-evidence.md);
- give every stateful command at least one test that starts from empty state (a fresh home, no planted config), and list each file the fixtures plant beside the production code that creates it. A planted file with no producer is missing behaviour, not test setup;
- commit its work on the branch following repository commit rules (or a configured custom commit skill), and push nothing.

A **destructive** slice runs on the stronger implementer profile the approved
plan names for it. On Herdr the default is the planner's harness, model and
effort with mode `auto`, or mode `default` when the planner runs Pi, whose only
supported mode is `default`. Pass it as the attempt's `requested_profile`, with
the plan approval as `profile_authorization` ([profile proof](profile-proof.md)).
Its repairs keep that profile.

Gates, each run by you:

1. **Green**: the full suite and linters pass, with the baseline's skips and no new ones.
2. **Red check**: in a throwaway checkout of each group's base subject commit, run only that group's named test with its filtered command. Each must fail for the intended reason: the behaviour under change, not an import error or missing fixture. A file-level failure is not red evidence: reject a run that executed more than the one named test, and reject a red produced by another test in the same file or by an intermediate commit. A group whose own test passes on the base is not behavioural; it is a **guard** only when the approved plan names it as protecting behaviour the change must keep, and such a guard passes on the base by design. Any other test that passes on the base proves nothing; send it back to the implementer with the evidence. Remove the throwaway checkout afterwards.
3. **Real-artifact smoke**: when the plan's end-to-end command prepares and validates the shipped artifact (a payload, package, installer or image), run it on the real artifact after the first slice that produces one and after each later slice that changes it, not only after the final review. A failure is that slice's gate failure.

### Review

Read [review.md](review.md) and run its shared review-and-repair loop with
this delivery's immutable base SHA and approved brief/plan. Keep Mention
findings for the PR. Gate: no must-fix findings remain, the reviewer examined
the final result, and your green run follows the last commit.

### QA

Run when the user did not skip it. Read [qa.md](qa.md).

Gate: QA's before-and-after evidence shows the change works in the real environment, and the starting state is restored.

A QA result that contradicts the brief (the bug does not reproduce, the fix exposes a new problem) is a scope change: stop, present the evidence and options with a recommendation, and resume with the user's decision through build and review.

## Ticket graph

Read [scheduling.md](scheduling.md) for ticket ownership, human schedules,
conflicts, failures and partial runs. Its frontier requires verified integration,
not merely a native worker completion.

1. Use the integration workspace from setup; do not create a second integration
   branch. Create each ticket workspace from the current integration tip at dispatch.
2. The **frontier** is every ticket whose blockers are merged into the integration branch. Start one implementer role per frontier ticket, at most the brief's limit at once (default 3), each with the build brief above scoped to its ticket.
3. When a ticket's build gates pass, merge its branch into the integration branch and run the full suite there. A failure goes back to that ticket's implementer before the next merge.
4. Refill the frontier as tickets land.
5. After the last ticket: one review of the whole integration branch against the spec, with all must-fix findings fixed by a single implementer role, then QA on the integration branch.

Gate: every ticket landed, the integration branch is green, the review has no must-fix finding, and QA passed or was skipped.
