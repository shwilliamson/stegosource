# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #11: Error recovery and workspace reset mechanism

## Context
- Mode: all-issues (auto-merge handled by orchestrator)
- This issue is about making the app resilient to broken agent-generated code and providing a reset mechanism
- Dependencies #5 (scaffold) and #9 (forms/controls) are both closed/complete

## Acceptance Criteria
1. If the agent writes code that crashes app.py, the error is caught and displayed to the user
2. The agent can detect when its edit broke something (via error output) and attempt a fix
3. A "Reset Workspace" button restores app.py's dynamic section to its default empty state
4. Reset preserves chat history in session state
5. The agent's system prompt includes guidance on writing valid Python and testing edits
6. If the dynamic section crashes, the scaffold (chat interface) still functions so the user can ask the agent to fix it

## Technical Notes from Issue
- The scaffold section should wrap the dynamic section import/execution in a try/except to catch errors gracefully
- The reset mechanism needs a copy of the original app.py dynamic section content (stored as a constant or separate file)
- The agent should be instructed to read app.py before editing to understand the current state
- Consider storing a backup of app.py before each agent edit (e.g., `app.py.bak`) for manual recovery
- Streamlit's error display is actually useful here -- showing the traceback helps the agent understand what went wrong

## Current Architecture

### app.py Structure
The app has two clearly marked sections:
1. **Scaffold section** (`# === SCAFFOLD START ===` to `# === SCAFFOLD END ===`): Chat interface, sidebar, session state, streaming agent response, error handling for agent calls. This section MUST NOT be broken.
2. **Dynamic section** (`# === DYNAMIC START ===` to `# === DYNAMIC END ===`): Agent's workspace. Currently contains example prompts and a centered empty state UI.

### Key Files
- `app.py` - Main Streamlit app (scaffold + dynamic section)
- `agent.py` - Agent SDK client, system prompt (`SYSTEM_PROMPT`), tool definitions
- `tests/test_app.py` - Tests for app module
- `tests/test_agent.py` - Tests for agent module (includes system prompt tests)

### Important Notes
- The dynamic section currently defines `EXAMPLE_PROMPTS`, `_send_example_prompt()`, and the empty state UI
- The scaffold section already has error handling for the agent SDK calls (AgentConfigError, AgentError, generic Exception)
- The system prompt already has a "Code Quality" section and an "Error Handling" section
- Existing tests verify scaffold markers, dynamic section content, session state, and system prompt contents

## Implementation Plan

### 1. Store Default Dynamic Section Content
Create a constant (e.g., `DEFAULT_DYNAMIC_CONTENT`) that holds the original dynamic section content. This could be:
- A constant string in a separate module (e.g., `dynamic_defaults.py`)
- Or defined at the top of app.py before the dynamic section

The default should be the current content between `# === DYNAMIC START ===` and `# === DYNAMIC END ===`.

### 2. Wrap Dynamic Section in try/except (in app.py)
The dynamic section code needs to be wrapped so that if it crashes:
- The error traceback is displayed to the user via `st.error()` or `st.exception()`
- The scaffold (chat interface in sidebar) still works
- The user can still chat with the agent to ask it to fix the broken code

**Approach:** Since Streamlit executes app.py top-to-bottom, the simplest approach is to extract the dynamic section into a function or use exec() with a try/except. However, given the markers-based approach, a better pattern is:
- Move the dynamic section content into a separate file (e.g., `dynamic_section.py`) that app.py imports inside a try/except
- OR: Keep it inline but wrap the dynamic section with a try/except block

The most practical approach given the current architecture: wrap the dynamic section code between the markers in a try/except directly in `app.py`. If the dynamic section code crashes, catch the exception and display it.

### 3. Add Reset Workspace Button
Add a "Reset Workspace" button in the sidebar (within the scaffold section, since it must always be accessible). When clicked:
- Read the default dynamic content
- Write it back to app.py (replacing everything between dynamic markers)
- Preserve chat history (session state is preserved across Streamlit reruns)
- Trigger a rerun

### 4. Update System Prompt in agent.py
Add guidance to SYSTEM_PROMPT about:
- Reading app.py before editing to understand current state
- Error recovery: if the hot-reload fails, the error will be visible and the agent should fix it
- The system already has "Code Quality" and mentions reading errors -- enhance this with explicit error recovery instructions

### 5. Add Backup Mechanism
Before each agent edit, the agent should create a backup (e.g., `app.py.bak`). This can be mentioned in the system prompt as a best practice.

### 6. Write Tests
- Test that the dynamic section is wrapped in error handling
- Test the reset mechanism (restoring default content)
- Test that chat history is preserved on reset
- Test that the system prompt includes error recovery guidance

## Resources (Read as Needed)
- Issue details: `gh issue view 11`
- Current app.py: `app.py`
- Current agent.py: `agent.py`
- Existing tests: `tests/test_app.py`, `tests/test_agent.py`
- Commands: `.claude/commands.md`

## Expected Output
- Working implementation matching all 6 acceptance criteria
- Tests passing (both existing and new)
- PR created with "Closes #11" in body
- Branch naming: `11-error-recovery-reset`
