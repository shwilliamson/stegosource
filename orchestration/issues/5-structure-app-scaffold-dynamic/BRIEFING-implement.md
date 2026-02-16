# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #5: Structure app.py with scaffold/dynamic sections and empty state

## Context
- Issue #5 in Milestone 1: Foundation & Agent Chat
- Dependencies #2 (Agent SDK client) and #3 (Chat interface) are both closed/merged
- Mode: all-issues

## Current State Analysis

The app.py already has:
- Scaffold markers (`# === SCAFFOLD START ===` / `# === SCAFFOLD END ===`) with page config, session state, chat interface, and agent connection logic
- Dynamic markers (`# === DYNAMIC START ===` / `# === DYNAMIC END ===`) but the dynamic section is EMPTY
- The agent.py system prompt already references the markers and instructs the agent to only modify the dynamic section

## What Needs To Be Implemented

The dynamic section needs to contain the **empty state** UI that shows when the agent has not yet modified the dynamic section. This includes:

1. **Empty state detection**: Check if the dynamic section content has been modified from its default. Since this IS the default content, it should display the empty state.

2. **Empty state UI** (per design-system.md):
   - Centered in main area using `st.columns([1,2,1])` for centering, max-width ~640px
   - Logo displayed via `st.image("logo.jpeg")`, max-width 280px, centered
   - Tagline: "Dynamic Data Visualization Agent" in text-secondary, caption size
   - 1-2 sentence description of what the app does, text-secondary, body size
   - 3-4 clickable example prompt cards in a 2x2 grid using `st.columns([1, 1])`

3. **Example prompt cards**:
   - Each is a `st.button()` with `use_container_width=True`
   - Prompts (from the issue):
     - "Show me AAPL stock for the last 3 months"
     - "Add a date range picker"
     - "Compare TSLA and F"
   - Plus one more from design-system.md:
     - "Create a candlestick chart for GOOGL"
   - On click, populate chat input and send the message

4. **Click behavior**: When a user clicks an example prompt button:
   - Set `st.session_state.messages.append({"role": "user", "content": prompt_text})`
   - Set `st.session_state.processing = True`
   - Set `st.session_state.pending_prompt = prompt_text`
   - Call `st.rerun()` to trigger the chat processing

## Technical Constraints

- The empty state code goes BETWEEN the `# === DYNAMIC START ===` and `# === DYNAMIC END ===` markers
- Use `st.button()` with callbacks that set session state variables
- The empty state should disappear once the agent modifies the dynamic section (but since this is the initial version, it will always show until the agent edits it)
- Follow the design system tokens and patterns from design-system.md
- The scaffold section must NOT be modified

## Acceptance Criteria (from issue)
- [ ] `app.py` has a clearly marked scaffold section with comments -- ALREADY DONE
- [ ] Scaffold section contains: page config, sidebar chat interface, agent connection logic, session state initialization -- ALREADY DONE
- [ ] Dynamic section is clearly marked -- ALREADY DONE
- [ ] Dynamic section initially contains the empty state: app description and clickable example prompts -- IMPLEMENT THIS
- [ ] Agent's system prompt references these markers and instructs it to only modify the dynamic section -- ALREADY DONE
- [ ] Clicking an example prompt populates the chat input and sends the message -- IMPLEMENT THIS
- [ ] 3-4 example prompts provided -- IMPLEMENT THIS

## Tests
- Update `tests/test_app.py` to add tests for the empty state functionality
- Test that the example prompts are defined
- Test the prompt click callback behavior
- Ensure existing tests still pass

## Resources (Read as Needed)
- Issue details: `gh issue view 5`
- Design system: `design-system.md` (especially the Empty State section)
- Existing app: `app.py`
- Existing tests: `tests/test_app.py`
- Commands: `.claude/commands.md`

## Expected Output
- Working implementation matching acceptance criteria
- Tests passing (`pytest`)
- Lint passing (`ruff check .`)
- PR created with "Closes #5" in body
- Branch name: `5-structure-app-scaffold-dynamic`
