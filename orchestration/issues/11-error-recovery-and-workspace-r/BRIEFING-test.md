# Agent Briefing: test
Generated: 2026-02-16

## Your Task
Verify PR #24 meets acceptance criteria for issue #11.

## Context
- Issue: #11 - Error recovery and workspace reset mechanism
- Developer has completed implementation with all tests passing

## Acceptance Criteria to Verify
1. If the agent writes code that crashes app.py, the error is caught and displayed to the user
2. The agent can detect when its edit broke something (via error output) and attempt a fix
3. A "Reset Workspace" button restores app.py's dynamic section to its default empty state
4. Reset preserves chat history in session state
5. The agent's system prompt includes guidance on writing valid Python and testing edits
6. If the dynamic section crashes, the scaffold (chat interface) still functions so the user can ask the agent to fix it

## Prior Agent Activity
- **Developer**: Implemented error recovery and workspace reset:
  - Created `dynamic_defaults.py` module with default content constant and `reset_dynamic_section()` function
  - Wrapped dynamic section in `app.py` with try/except to catch crashes gracefully
  - Added "Reset Workspace" button in sidebar scaffold section
  - Enhanced system prompt with Error Recovery section and read-before-edit guidance
  - Added 38 new tests (277 total, all passing)

## Resources (Read as Needed)
- PR details: `gh pr view 24`
- Issue acceptance criteria: `gh issue view 11`
- Test commands: Check `.claude/commands.md`
- Run tests: `pytest`

## Expected Output
Post standardized review comment on PR #24:
- APPROVED - Tester (all tests pass, criteria verified)
- CHANGES REQUESTED - Tester (issues found)

After completing verification, write your report to:
orchestration/issues/11-error-recovery-and-workspace-r/REPORT-test.md
