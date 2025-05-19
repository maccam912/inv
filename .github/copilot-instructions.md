This is a python project that uses hatch for testing and packaging. Continue to use hatch where possible. Use UV if necessary.

Always work according to the plan in the README.md file. If you are unsure about the plan, ask for clarification.
If you need to make changes to the plan, discuss them with the team first.

This should use textual for the TUI, sqlite for the database.

Always write testable code, and add unit tests. Also document your code with docstrings.

Use types where possible.

`hatch run check` can be used to check for type errors, linting issues, and formatting problems, plus run tests.
It all must be passing before a PR can be merged.