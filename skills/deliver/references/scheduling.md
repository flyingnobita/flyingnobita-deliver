# Tickets and human work

Use for ticket graphs and whenever intake finds user-only steps. The
orchestrator owns scheduling, shared tracker state and integration merges.

## Before the grilling stop

Read every ticket and its blocking edges. Reject missing blockers or cycles
before dispatch. Identify human tickets, human steps embedded in agent tickets,
and likely questions from vague acceptance criteria or always-ask areas.
Settle the questions at grilling; split or front-load embedded human steps
when needed. Load `wizard` (or `mattpocock-wizard`) for steps only the user can perform.

Offer a schedule only when human work exists:

- **normal:** start ready agent tickets; notify whenever human work becomes ready.
- **front-load:** prioritize available human work while independent agent work
  proceeds. Explain blockers that prevent doing all human work first.
- **back-load:** finish work independent of human tickets first, then notify
  once and wait for human work and its dependents.

Every schedule preserves dependencies. If two schedules produce the same
order, explain that rather than promising fewer interruptions. The brief stores
the schedule and effective concurrency from [configuration.md](configuration.md).

## State and dispatch

Read the repo's tracker convention. For local tickets, use `git ls-files` to
decide whether they are tracked. Tracked status changes belong on the integration
branch; ignored `.scratch` records stay at the originating checkout's absolute
path. Give workers that location explicitly. Preserve GitHub issue identities
when that is the tracker. Runtime evidence stays outside disposable worktrees.

Only the orchestrator changes statuses. Workers may append comments to their
own ticket. Claim a ticket before creating its worktree or dispatching it;
commit the claim first when tracked, following repository commit rules (or a configured custom commit skill).
Each worker branches from the current integration tip. Record actual branch,
workspace and task identities instead of assuming a naming convention.

Close the finished gate task before dispatching repair. A completed review
still holds a worker slot until it is verified, so with `max_workers` reached
the repair `attempt` is refused with `concurrency limit reached`: verifying the
gate task, or abandoning it with the user's recorded decision, is the step
before opening the repair attempt, and the verified gate releases its slot
first.

The frontier contains ready agent tickets whose blockers are **verified and
merged**, excluding schedule-held tickets. Native task completion alone never
unblocks delivery. Merge one ticket at a time after its independent build gates;
run the full suite on the integration result before resolving the ticket.
Shared changelog/docs edits have one assigned owner, normally an implementer
follow-up after integration, rather than concurrent ticket writers.

On conflict, abort the orchestrator's merge and return the conflict to that
ticket's implementer: merge the current integration tip, resolve, test and
commit. Verify its new result before attempting the integration merge again.

## Questions, failures and human hand-back

Answer from approved decisions and the code when they settle the question.
Unresolved scope and permission decisions stop dependent work and go to the
user. Continue independent work only when the answer cannot affect it. A
timeout leaves the question pending; it never grants an assumption or approval.

A worker reporting failure moves its ticket to `needs-info` with evidence;
hold its transitive dependents while independent tickets continue. A process or
transport failure is reconciled through the adapter before any retry. Keep
uncertain work and resource identities intact.

Human requests name the integration worktree and exact acceptance criteria.
When the user reports completion, inspect the committed result or external
evidence, verify acceptance, then resolve the ticket and refill the frontier.
Notify through the selected adapter; never claim an OS notification was seen.

## Wrap up and resume

On "wrap up", stop dispatching new tickets and let active workers settle.
Review and test the landed subset, report unresolved/skipped/human tickets and
retain the integration workspace and evidence. Mark the run partial; do not
ship it as satisfying the original brief. Shipping a smaller scope requires
the user's revised brief and plan approval.

On resume, validate host, approvals, integration SHA, ticket state and native
workers. A resolved status alone is not proof its commit remains integrated.
Reattach live workers, process settled results, and restart only through the
adapter's proven recovery path. Never restart merely because a tab vanished.
