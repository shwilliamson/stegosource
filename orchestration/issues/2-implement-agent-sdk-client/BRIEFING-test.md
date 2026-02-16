# Agent Briefing: test
Generated: 2026-02-16

## Your Task
Verify PR #14 meets acceptance criteria for issue #2.

## Context
- Issue: #2 - Implement Agent SDK client with streaming and system prompt
- This is a backend/SDK integration issue (no UI to test visually)
- Developer has 40 passing unit tests

## Prior Agent Activity
- **Developer**: Implemented `agent.py` with Agent SDK client, streaming support, system prompt, error handling. 40 tests passing, lint clean. PR #14.

## Acceptance Criteria to Verify
- [ ] `agent.py` implements `ClaudeSDKClient` connection with streaming enabled
- [ ] System prompt defines the agent's role: Stegosource, data visualization assistant
- [ ] System prompt instructs the agent to preserve the scaffold section and only modify dynamic section
- [ ] Agent has access to built-in tools: Read, Write, Edit, Bash
- [ ] Conversation history stored in a format suitable for replay across Streamlit reruns
- [ ] `asyncio.run()` bridges async SDK calls into Streamlit's sync execution model
- [ ] API key loaded from `.env` via `python-dotenv`
- [ ] Graceful error handling if `ANTHROPIC_API_KEY` is missing or invalid

## Verification Steps
1. Read the PR diff: `gh pr diff 14`
2. Check that all unit tests pass: `pytest tests/test_agent.py -v`
3. Check lint: `ruff check .`
4. Verify each acceptance criterion against the implementation
5. Verify the system prompt content addresses scaffold preservation
6. Verify error handling for missing API key

Note: This is not a UI issue so no Playwright/browser testing is needed. Focus on code review and running existing tests.

## Resources (Read as Needed)
- PR details: `gh pr view 14`
- PR diff: `gh pr diff 14`
- Issue acceptance criteria: `gh issue view 2`
- Test commands: Check `.claude/commands.md`

## Expected Output
Post standardized review comment on PR #14:
- APPROVED - Tester (all tests pass, criteria verified)
- CHANGES REQUESTED - Tester (issues found)

Write report to: orchestration/issues/2-implement-agent-sdk-client/REPORT-test.md
