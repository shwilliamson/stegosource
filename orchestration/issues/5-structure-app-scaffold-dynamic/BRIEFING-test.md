# Agent Briefing: test
Generated: 2026-02-16

## Your Task
Verify PR #16 meets acceptance criteria for issue #5.

## Context
- Issue: #5 - Structure app.py with scaffold/dynamic sections and empty state
- This is the final piece of Milestone 1: Foundation & Agent Chat

## Prior Agent Activity
- **Developer**: Added empty state UI to the dynamic section of app.py. Implementation includes EXAMPLE_PROMPTS list with 4 prompts, _send_example_prompt() callback, and centered layout using st.columns([1,2,1]) with logo, tagline, description, and 2x2 grid of example prompt buttons. Added 9 new tests.

## Acceptance Criteria to Verify
- [ ] `app.py` has a clearly marked scaffold section with comments (e.g., `# === SCAFFOLD START ===` / `# === SCAFFOLD END ===`)
- [ ] Scaffold section contains: page config, sidebar chat interface, agent connection logic, session state initialization
- [ ] Dynamic section is clearly marked (e.g., `# === DYNAMIC CONTENT START ===` / `# === DYNAMIC CONTENT END ===`)
- [ ] Dynamic section initially contains the empty state: app description and clickable example prompts
- [ ] Agent's system prompt references these markers and instructs it to only modify the dynamic section
- [ ] Clicking an example prompt populates the chat input and sends the message
- [ ] 3-4 example prompts provided: "Show me AAPL stock for the last 3 months", "Add a date range picker", "Compare TSLA and F"

## Resources (Read as Needed)
- PR details: `gh pr view 16`
- PR diff: `gh pr diff 16`
- Issue details: `gh issue view 5`
- Test commands: Check `.claude/commands.md`

## Expected Output
1. Run tests: `pytest`
2. Run lint: `ruff check .`
3. Start dev server and use Playwright MCP to verify the empty state renders correctly
4. Post standardized review comment on PR #16:
   - APPROVED - Tester (all tests pass, criteria verified)
   - CHANGES REQUESTED - Tester (issues found)

After completing verification, write your report to:
orchestration/issues/5-structure-app-scaffold-dynamic/REPORT-test.md
