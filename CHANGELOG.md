# Changes

- Nov-10, 2026 - 04:46 PM +08 - Allow native Orca orchestration guide directly without requiring a local discovery stub; document Orca executable resolution and public installation routes.

- Nov-10, 2026 - 04:42 PM +08 - Fix Skills CLI update documentation in README to use installed skill names and clarify branch-tip versus tagged release installation; update Orca prerequisite guidance to reference bundled orchestration install command and official URLs.

- Nov-10, 2026 - 04:30 PM +08 - Release v0.1.0: Publish the delivery suite as a standalone installable public repository covering Deliver, Setup, Review, and Retro. Refreshed skills from production dotfiles without orphaned dagr references; made identity, org access, and contribution routing portable; replaced mandatory personal commit dependencies with repository commit rules and optional custom commit skill support; added dual upstream/prefixed dependency resolution; removed private fleet pointers and paths; added README and MIT license; and adapted complete runtime and preflight test suites.

- Oct-28, 2026 - 11:45 AM +08 - Refer to Matt Pocock skills by their upstream names (`grilling`, `tdd`) instead of fleet-prefixed `mattpocock-*` names, and note how to tell `code-review` apart from a harness built-in.

- Oct-28, 2026 - 11:41 AM +08 - Copy the flyingnobita-deliver, -setup, -review and -retro skills and the helper tests from the dotfiles repo at ebe6374, as the future public source; dotfiles stays authoritative until the scheduled migration.
