# Agent Report: design-specs
Completed: 2026-02-16

## What Was Done
Posted design specifications as a comment on issue #4. The specs leverage the existing design system's "Tool Call Display" section and provide detailed implementation guidance.

## Key Design Decisions
1. **st.status() over st.expander()** for live streaming — natively supports running/complete/error states
2. **st.expander()** for chat history replay — simpler, static display
3. **Friendly labels** with Material icons for each tool type (Edit, Read, Bash, etc.)
4. **Data model extension** — messages store `tool_calls` list alongside `content` text
5. **Truncated results** — tool output capped at 500 chars to keep chat readable
6. **format_tool_label() helper** — centralizes label/icon generation logic

## Design Artifacts
- Issue comment with full design specifications posted to #4
- Tool type mapping table (tool name → friendly label + Material icon)
- Component state definitions (running, complete, error)
- Data model for storing tool calls in session state
- Accessibility requirements documented
