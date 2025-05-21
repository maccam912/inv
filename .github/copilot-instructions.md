Project Tooling

Use Hatch for all testing, packaging, and environment management.

Do not use pip install directly—there’s a firewall blocking internet access. All deps must be managed offline or via Hatch.

If you absolutely must, you may fall back to UV, but Hatch is the first choice.

Follow the Plan

Always work from README.md.

If the README is unclear, ask immediately—do not make assumptions.

If you think the plan needs updating, propose changes to the team before coding.

Architecture Choices

TUI library: use textual.

Database: use SQLite.

Code Quality

Write testable functions and modules.

Add thorough unit tests alongside your code.

Document every function, class, and module with docstrings.

Use type hints everywhere reasonable.

Pre-PR Checks

Before creating any Pull Request:

Run uvx hatch run check locally.

Fix all errors and warnings.

Never skip this step—PRs with failing checks are rejected automatically.

Branch & Commit Best Practices

Use feature/ or bugfix/ prefixes in branch names (e.g., feature/add-login).

Write clear, concise commit messages:

Title: short summary (50 chars max).

Body (optional): explain “why,” not “what.”

PR Etiquette

Include a brief description of:

What you’ve done.

Why you made any design decisions.

Link to any relevant issue or discussion.

If your change affects documentation, update README or docs too.

Continuous Integration

Ensure your code passes CI pipelines (linting, formatting, tests) on the remote before requesting review.

🚨 IMPORTANT
Always run:

uvx hatch run check
locally and confirm zero errors before opening a PR.
A PR with failing checks will be rejected—so run the checks every time!