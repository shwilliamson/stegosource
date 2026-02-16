# Agent Briefing: architect-review
Generated: 2026-02-16

## Your Task
Review PR #20 for technical quality.

## Context
- Issue: #7 - Agent generates Plotly charts via file editing and hot-reload
- Developer has completed implementation

## Prior Agent Activity
- **Developer**: Enhanced the agent's system prompt in `agent.py` with a comprehensive "Chart Generation Patterns" section including line chart, candlestick, and multi-symbol comparison examples. Created a new `chart_theme.py` module with reusable Plotly theming constants (`STEGO_LAYOUT`, `CHART_COLORS`, `CANDLESTICK_UP/DOWN`). Added 14 new system prompt tests and 15 chart theme tests (including Plotly integration tests). All 187 tests pass, lint clean.

## Resources (Read as Needed)
- PR details: `gh pr view 20`
- PR diff: `gh pr diff 20`
- Issue details: `gh issue view 7`
- Design system: `design-system.md` (for color token verification)

## Expected Output
Post standardized review comment on PR #20:
- APPROVED - Architect (if acceptable)
- CHANGES REQUESTED - Architect (if issues found)
