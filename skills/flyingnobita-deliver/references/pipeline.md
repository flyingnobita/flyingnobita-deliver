# Pipeline

This follows Matt Pocock's implement workflow (`implement`, `implement-spec`) with the user's profiles: one implementer drives `tdd` at the seams approved at the plan stop, commits, and `code-review` reviews. Your own checks sit on top of it.

Roles and their profiles come from the adapter. Every role brief:

- points to the brief, the approved plan, and its seams rather than restating them;
- asks for a numbered report: what changed, each command run and its result.

Verify each gate yourself in the work's workspace. A role's report tells you where to look; your own run is the evidence.

## Single unit

### Build

Start the implementer role. Its brief:

- load `tdd` and work in vertical red-green slices, testing only at the seams listed in the approved plan; those seams are already confirmed with the user, so it starts without asking;
- run single test files as it goes, then the full suite, linters and the repo's pre-commit hooks at the end;
- commit its work on the branch with `flyingnobita-clean-commit`, and push nothing.

Gates, each run by you:

1. **Green**: the full suite and linters pass, with the baseline's skips and no new ones.
2. **Red check**: in a throwaway checkout of the base commit, run the new and changed tests. Each must fail for the intended reason: the behaviour under change, not an import error or missing fixture. The exception is a **guard**: a test the approved plan names as protecting behaviour the change must keep, which passes on the base by design. Any other test that passes on the base proves nothing; send it back to the implementer with the evidence. Remove the throwaway checkout afterwards.

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
