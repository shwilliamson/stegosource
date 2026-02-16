# Agent Briefing: design-specs
Generated: 2026-02-16

## Your Task
Add UI/UX specifications to issue #3 (Build Streamlit chat interface with streaming display).

## Context
- Issue: #3 - Build Streamlit chat interface with streaming display
- This issue involves building a chat interface in the Streamlit sidebar for interacting with an agent, with streaming responses
- The agent SDK client (issue #2) is already implemented in `agent.py` with both sync and async streaming functions
- There is a comprehensive `design-system.md` already defining the visual language for the app

## Acceptance Criteria from Issue
- Chat input widget in the Streamlit sidebar using `st.chat_input()`
- Chat history displayed using `st.chat_message()` with user/assistant roles
- Conversation state persisted in `st.session_state` (survives Streamlit reruns and hot-reloads)
- Agent responses stream progressively (typewriter effect) as they arrive
- Loading indicator shown while the agent is processing ("Thinking...")
- Chat history scrolls to show the latest message

## Resources (Read as Needed)
- Issue details: `gh issue view 3`
- design-system.md: Available design tokens and patterns (comprehensive, already created)
- Existing `app.py`: Current minimal scaffold
- `agent.py`: Agent SDK client with `query_agent_streaming()`, `extract_assistant_text()`, etc.
- The sidebar layout section of design-system.md defines chat component patterns

## Technical Constraints
- Streamlit sidebar has limited width (~300-500px) -- keep formatting compact
- `st.chat_message()` and `st.chat_input()` are the standard Streamlit chat components
- Session state must survive hot-reloads (when the agent edits app.py)
- Streaming can use `st.empty()` or `st.write_stream()` for progressive rendering
- The app uses `layout="wide"` page config
- No `.streamlit/config.toml` exists yet -- should be created per design system specs

## Expected Output
Post design specifications as an issue comment following your AGENT.md template, including:
- Design intent
- User flow
- Visual design with token references from design-system.md
- Component states (empty, loading, streaming, error)
- Accessibility requirements
- Responsive behavior
- Specific Streamlit implementation patterns
