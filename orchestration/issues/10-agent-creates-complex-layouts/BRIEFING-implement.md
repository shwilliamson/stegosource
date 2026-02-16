# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #10: Agent creates complex layouts: dashboards, columns, and tabs

## Context
- This is a system prompt enhancement issue. The agent needs patterns and examples for generating complex Streamlit layouts.
- The established pattern: add a new section to `SYSTEM_PROMPT` in `agent.py` with layout patterns and examples, then add corresponding tests in `tests/test_agent.py`.
- Issue #9 (Forms and controls) is complete and its pattern was: add "Form and Widget Generation Patterns" section to the system prompt with key principles, examples for each widget type, modify/remove guidance, and a checklist.
- Mode: all-issues (auto-merge handled by orchestrator)

## Acceptance Criteria (from issue)
- [ ] Agent can create multi-column layouts using `st.columns()`
- [ ] Agent can create tabbed interfaces using `st.tabs()`
- [ ] Agent can build a dashboard with multiple charts (e.g., "Compare top 5 tech stocks")
- [ ] Agent can use `st.container()`, `st.expander()`, and other layout primitives
- [ ] Complex layouts render correctly after hot-reload
- [ ] Agent can iteratively build up complexity ("start with AAPL, now add MSFT, now put them side by side")

## Technical Notes (from issue)
- This is the "wow" moment of the demo -- the agent building real, complex layouts from natural language
- The agent needs to manage increasingly complex code in the dynamic section of app.py
- Streamlit layout containers must be nested correctly (columns inside containers, etc.)
- The agent should be able to read the current app.py to understand what it's already built before making additions
- Performance consideration: too many API calls in a single dashboard could hit rate limits

## What to Implement

### 1. Add "Complex Layout Patterns" section to SYSTEM_PROMPT in `agent.py`

Add a new section AFTER the existing "Widget Checklist" section (at the end of the Form and Widget section), and BEFORE the closing `"""` of the system prompt. The new section should include:

#### Key Principles
- How to use `st.columns()` for side-by-side layouts
- How to use `st.tabs()` for tabbed interfaces
- How to use `st.container()` for grouping
- How to use `st.expander()` for collapsible sections
- Nesting rules (columns inside containers, etc.)
- Reading current app.py before making additions (iterative building)
- Performance considerations for dashboards with many API calls

#### Required Examples (each should be self-contained with error handling, theme imports)
1. **Multi-Column Layout** - Side-by-side charts using `st.columns()`
2. **Tabbed Interface** - Multiple views using `st.tabs()`
3. **Dashboard with Multiple Charts** - Full dashboard combining columns, containers, and multiple charts (the "wow" example with tech stocks)
4. **Expander Layout** - Collapsible sections using `st.expander()`
5. **Iterative Building Guidance** - How to read existing code and add to it incrementally

#### Layout Checklist
Similar to Chart Checklist and Widget Checklist, add a Layout Checklist for pre-save verification.

#### Modifying/Removing Layouts
Similar to existing "Modifying Existing Charts" and "Modifying or Removing Controls" sections.

### 2. Add tests in `tests/test_agent.py`

Add a new test section `# --- Complex Layout Patterns Tests ---` (following the pattern of `# --- Form and Widget Generation Tests ---`) that verifies:
- Section title exists in SYSTEM_PROMPT
- `st.columns()` usage is documented
- `st.tabs()` usage is documented
- `st.container()` usage is documented
- `st.expander()` usage is documented
- Multi-column example is present
- Tabbed interface example is present
- Dashboard example is present
- Layout examples use error handling
- Layout examples use STEGO_LAYOUT theme
- Layout examples use fetch_daily
- Layout checklist is present
- Iterative building guidance is present
- Nesting guidance is present
- Modifying/removing layouts guidance is present

### 3. Run tests and ensure they pass
```bash
pytest tests/test_agent.py -v
```

### 4. Run linter
```bash
ruff check . && ruff format .
```

## Resources (Read as Needed)
- Issue details: `gh issue view 10`
- Current agent.py: Read the SYSTEM_PROMPT to see existing patterns
- Current tests: Read tests/test_agent.py for test patterns
- `.claude/commands.md` for test/lint commands

## Expected Output
- Working implementation matching acceptance criteria
- Tests passing
- PR created with "Closes #10" in body
