# Your first delivery on Herdr

Use a small Python repository you own, with a clean working tree and a remote default branch. Choose a repository without existing `parity.py` or `test_parity.py` files. This task uses only Python's standard library.

## 1. Complete setup

Follow the README's [Quick start](../README.md#quick-start), expanding the Herdr section. Continue only after setup validates the selected profiles. Keep `max_workers = 1` and `landing = "leave"` for this example.

## 2. Give Codex this task inside Herdr

```text
deliver add a small parity helper:
- Create parity.py with is_even(value: int) -> bool for integer inputs.
- Return True for even integers, including zero and negative even integers.
- Return False for odd integers, including negative odd integers.
- Add test_parity.py using unittest, covering 0, 2, 3, -2 and -3.
- Build test-first and run python3 -m unittest test_parity.py.
- Add no dependencies and change no existing application behavior.
- Keep landing = "leave": report the committed local branch without pushing,
  opening a PR or merging. Skip optional live-environment QA for this task.
```

Answer any remaining brief questions and approve the plan. The expected result is the helper, its tests, and a report naming the branch, commit and verification results. Repository rules may require additional checks or documentation.

## 3. Check the result

In the delivery workspace named in the report, run:

```bash
python3 -m unittest test_parity.py
git log -1 --oneline
git status --short
```

Tests should pass. Read `parity.py` and `test_parity.py` to confirm all five cases are covered, then compare the branch against the base commit recorded in the delivery report. Confirm the report includes independent review and verification, and explains any retained files or unfinished work.

A successful first delivery produces reviewed, committed code and passing tests on the local branch. Publishing or merging is a separate decision.
