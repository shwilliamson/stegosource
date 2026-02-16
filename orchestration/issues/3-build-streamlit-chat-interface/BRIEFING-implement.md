# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #3: Build Streamlit chat interface with streaming display

## Context
- Mode: all-issues (auto-merge handled by orchestrator)
- Dependency #2 (Agent SDK client) is merged and available in `agent.py`
- Designer has provided specifications (see issue comments)

## Acceptance Criteria
- Chat input widget in the Streamlit sidebar using `st.chat_input()`
- Chat history displayed using `st.chat_message()` with user/assistant roles
- Conversation state persisted in `st.session_state` (survives Streamlit reruns and hot-reloads)
- Agent responses stream progressively (typewriter effect) as they arrive
- Loading indicator shown while the agent is processing ("Thinking...")
- Chat history scrolls to show the latest message

## Prior Agent Activity
- **Designer**: Created UI specifications including:
  - Sidebar layout with logo at top, chat messages below, input at bottom
  - 🦕 emoji as assistant avatar
  - Session state structure: `messages` list + `processing` boolean
  - Streaming via `st.empty()` with progressive markdown + ▌ cursor
  - `.streamlit/config.toml` must be created for theming
  - Scaffold/dynamic section markers in `app.py` for agent self-modification zones

## Technical Implementation Guide

### Files to Create/Modify
1. **`.streamlit/config.toml`** - Create with theme from design-system.md
2. **`app.py`** - Complete rewrite with chat interface scaffold

### Key Implementation Details

#### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#00D4FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1A1D26"
textColor = "#FAFAFA"
font = "sans serif"
```

#### `app.py` Structure
The file must have clearly marked scaffold and dynamic sections:
```python
# === SCAFFOLD START ===
# (Chat interface, imports, session state - agent must NOT modify)
# === SCAFFOLD END ===

# === DYNAMIC START ===
# (Agent-generated UI goes here)
# === DYNAMIC END ===
```

#### Streaming Pattern
- `query_agent_streaming()` is an async generator from `agent.py`
- Streamlit is synchronous - need to bridge async with `asyncio.run()` or event loop handling
- Use `st.empty()` container and update it progressively as text chunks arrive
- Show ▌ cursor during streaming, remove when complete

#### Session State
```python
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False
```

#### Agent module functions to use
- `query_agent_streaming(user_message, conversation_history)` - async generator yielding messages
- `extract_assistant_text(messages)` - extracts text from AssistantMessage objects
- `AgentError`, `AgentConfigError`, `AgentQueryError` - error classes

### Important Notes
- The sidebar has limited width (~350px) - keep message formatting compact
- No custom CSS needed beyond the config.toml theme
- Handle the case where ANTHROPIC_API_KEY is not set gracefully (show st.error)
- `st.chat_input()` must be called at the sidebar level, not inside conditionals that could prevent it from rendering
- All chat rendering must happen inside `with st.sidebar:`

## Resources (Read as Needed)
- Issue details: `gh issue view 3`
- Design specs: Check issue #3 comments for "**[Designer]** Design Specifications"
- design-system.md: Available design tokens
- `agent.py`: Agent SDK client with streaming support
- `tests/test_agent.py`: Existing test patterns

## Expected Output
- Working chat interface with streaming display
- `.streamlit/config.toml` created
- `app.py` rewritten with scaffold/dynamic sections
- Tests for chat-related utility functions (if any new ones created)
- PR created with "Closes #3" in body
- Branch named `3-build-streamlit-chat-interface`
