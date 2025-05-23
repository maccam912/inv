# AI Copilot Development Instructions

## Project Environment and Tooling

**Primary tool:** Use Hatch for all testing, packaging, and environment management.

**Important:** Do not use `pip install` directly due to firewall restrictions blocking internet access. All dependencies must be managed offline or through Hatch.

**Fallback option:** You may use UV if absolutely necessary, but Hatch is the preferred and primary choice.

## Project Planning and Requirements

**Always follow the plan:** Work exclusively from the README.md file as your source of truth.

**When unclear:** If the README contains ambiguous or missing information, ask for clarification immediately. Do not make assumptions or guess at requirements.

**Plan changes:** If you believe the project plan needs updating or modification, propose changes to the team before writing any code.

## Architecture and Technology Stack

**User Interface:** Use the Textual library for all terminal user interface (TUI) components.

**Database:** Use SQLite for all data storage requirements.

## Code Quality Standards

**Function design:** Write functions and modules that are easily testable and maintainable.

**Testing requirements:** Add comprehensive unit tests alongside all code you write. When fixing bugs, always include regression tests to prevent the same issue from recurring.

**Documentation:** Every function, class, and module must include clear docstrings explaining purpose, parameters, return values, and usage.

**Type safety:** Use type hints throughout the codebase wherever they add clarity and safety.

## Pre-Pull Request Validation

**Mandatory check:** Before creating any Pull Request, you must run `uvx hatch run check` locally.

**Fix all issues:** Address every error and warning reported by the check command.

**No exceptions:** This step is non-negotiable. Pull Requests with failing checks will be automatically rejected.

## Branch Naming and Commit Standards

**Branch naming:** Use descriptive prefixes for all branches:
- `feature/` for new functionality (example: `feature/add-user-authentication`)
- `bugfix/` for bug fixes (example: `bugfix/fix-login-validation`)

**Commit message format:**
- Title line: Concise summary in 50 characters or less
- Body (optional): Explain the reasoning behind the change, not just what was changed

## Pull Request Guidelines

**Required information in PR description:**
- Clear explanation of what you implemented or changed
- Justification for any significant design decisions made
- Links to relevant issues, discussions, or documentation

**Documentation updates:** If your changes affect user-facing functionality or developer workflows, update the README or relevant documentation files.

## Continuous Integration Requirements

**Pipeline compliance:** Ensure your code passes all CI pipeline checks including linting, formatting, and automated tests before requesting review.

**Local validation:** Always run `uvx hatch run check` locally and confirm zero errors before opening any Pull Request.

**Quality gate:** Pull Requests with failing checks will be rejected automatically, so validate locally every time.

## Key Reminders for AI Assistants

1. **Never skip the check command** - `uvx hatch run check` must pass before any PR
2. **Always add regression tests** when fixing bugs to prevent recurrence
3. **Ask for clarification** rather than making assumptions about unclear requirements
4. **Follow the established architecture** - use Textual for UI and SQLite for data
5. **Use Hatch as the primary tool** for all environment and dependency management
