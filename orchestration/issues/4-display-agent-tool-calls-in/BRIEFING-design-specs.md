# Agent Briefing: design-specs
Generated: 2026-02-16

## Your Task
Add UI/UX specifications to issue #4 (Display agent tool calls in the chat UI).

## Context
- Issue: #4 - Display agent tool calls in the chat UI
- This issue involves UI work and needs design specifications before implementation
- The design system is already documented in `design-system.md` and already has a "Tool Call Display" section

## What the Issue Requires
- Tool calls displayed in the chat alongside agent text responses
- Each tool call shown in an expandable/collapsible section (e.g., `st.expander`)
- Tool call display includes: tool name, key parameters, and result summary
- Tool calls appear in real-time as the agent streams (not only after completion)
- Visual distinction between tool calls and regular text (different styling or icon)
- Common tool calls have friendly labels: "Editing app.py...", "Running command...", "Reading file..."

## Technical Context
The Agent SDK yields these message types during streaming:
- `AssistantMessage` with content blocks: `TextBlock`, `ToolUseBlock`, `ToolResultBlock`
- `StreamEvent` with partial updates (for streaming)
- `ResultMessage` at the end

Tool-related types:
- `ToolUseBlock`: `id`, `name`, `input` dict
- `ToolResultBlock`: `tool_use_id`, `content`, `is_error` flag

The current `app.py` collects all messages and only renders the concatenated text. The streaming function `_stream_agent_response()` already iterates over the async generator but doesn't surface tool calls.

## Resources (Read as Needed)
- Issue details: `gh issue view 4`
- `design-system.md`: Already has a "Tool Call Display" section with icons, labels, and styling guidance
- Current `app.py`: The sidebar chat rendering code (within SCAFFOLD markers)
- `agent.py`: Contains `extract_tool_calls()` helper and message types

## Expected Output
Post design specifications as an issue comment following your AGENT.md template, including:
- Design intent
- User flow (how tool calls appear during streaming)
- Visual design with token references from design-system.md
- Component states (loading, completed, errored tool calls)
- Accessibility requirements
- Responsive behavior
- Specific Streamlit component recommendations (`st.status`, `st.expander`, etc.)
