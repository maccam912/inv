This is a python project that uses hatch for testing and packaging. Continue to use hatch where possible. Use UV if necessary.

Always work according to the plan in the README.md file. If you are unsure about the plan, ask for clarification.
If you need to make changes to the plan, discuss them with the team first.

This should use textual for the TUI, sqlite for the database.

Always write testable code, and add unit tests. Also document your code with docstrings.

Use types where possible.

All code checks must pass before you submit a PR for review. Before asking for reviews, run `uvx hatch run check` and fix any errors you have. Any PR which does not pass these checks will be rejected, so do yourself a favor and run the checks before you claim to be finished.

*** IMPORTANT: ALWAYS run `uvx hatch run check` locally to verify that all checks pass before submitting your work. Never skip this step! A PR with failing checks will be automatically rejected. ***