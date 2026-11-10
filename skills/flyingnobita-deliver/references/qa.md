# QA

QA proves the change in a real environment: a host, a container, a device. The user named the target at the grilling stop.

## Brief for the QA role

The QA role runs with full access, so its brief carries these guardrails verbatim:

- Record the starting state first: for Docker, `docker ps -a` and `docker images`; otherwise the equivalent inventory.
- Prefix every resource it creates (containers, temp dirs, images it pulls) with `qa<work-id>-`, and touch nothing it did not create. Read-only inspection of existing resources is fine.
- Use its own ports and networks so it never shares them with running services.
- Write only inside its own prefixed temp directories.
- Remove everything it created, also on failure, and prove the inventory matches the starting state.

## Method

1. **Before**: run the unchanged code and reproduce the problem. If it does not reproduce, stop and report: that is a scope change for the orchestrator.
2. **After**: run the changed code the same way, observe long enough to see repeated behaviour (at least one minute for anything periodic), and capture the evidence that the problem is gone.
3. Collect evidence a reviewer can check: commands, exit codes, API responses trimmed to what matters, log counts and excerpts.
   Retain the exact reproducible driver, executable version, mode and fixtures.
   For enforcement claims, require the allowed operation to succeed and the
   denied operation to fail in the same qualified run. Name unqualified variants.
   Keep failed shipped-driver receipts distinct from a successful focused probe.
4. Clean up and prove the starting state is restored.

Send follow-up runs to the same QA role so it keeps what it learned about the environment.

If independent reproduction fails, QA owns diagnosis and returns a corrected,
retained reproduction. Repository harness fixes go to the implementer through
the orchestrator; installed application files stay untouched. Before native
startup, isolate configuration, cache, trust and daemon paths that the CLI may
write. Investigate unexpected persistent-state changes without assigning an
actor from hashes alone; preserve the original failed preservation interval.
