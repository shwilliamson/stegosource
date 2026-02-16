# Agent Briefing: test
Generated: 2026-02-16

## Your Task
Verify PR #20 meets acceptance criteria for issue #7.

## Context
- Issue: #7 - Agent generates Plotly charts via file editing and hot-reload
- This is a system prompt enhancement + chart theming module. The changes are backend/agent configuration, not runtime UI changes.

## Prior Agent Activity
- **Developer**: Enhanced system prompt with chart generation patterns. Created `chart_theme.py` with Plotly theming. Added 29 new tests (14 system prompt, 15 chart theme including Plotly integration tests). All 187 tests pass.

## Verification Steps
1. Run `pytest` to verify all tests pass
2. Run `ruff check .` to verify lint passes
3. Review the system prompt changes in `agent.py` to confirm chart patterns are complete and correct
4. Review `chart_theme.py` to confirm theming constants match `design-system.md` values
5. Verify acceptance criteria coverage:
   - System prompt contains line chart example with `px.line`
   - System prompt contains candlestick chart example with `go.Candlestick`
   - System prompt references `st.plotly_chart(fig, use_container_width=True)`
   - System prompt includes chart titles, axis labels, and legends
   - System prompt includes error handling patterns
   - System prompt includes chart modification guidance
   - System prompt references Alpha Vantage data fetching
6. Start the dev server (`streamlit run app.py --server.runOnSave=true`) and verify app loads without errors
7. Verify the chart_theme module is importable: `python -c "from chart_theme import STEGO_LAYOUT; print('OK')"`

## Resources (Read as Needed)
- PR details: `gh pr view 20`
- PR diff: `gh pr diff 20`
- Issue acceptance criteria: `gh issue view 7`
- Test commands: Check `.claude/commands.md`

## Expected Output
Post standardized review comment on PR #20:
- APPROVED - Tester (all tests pass, criteria verified)
- CHANGES REQUESTED - Tester (issues found)
