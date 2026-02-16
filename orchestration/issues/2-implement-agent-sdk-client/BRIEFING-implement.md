# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #2: Implement Agent SDK client with streaming and system prompt

## Context
- This is the core Agent SDK integration piece for the Stegosource project
- Stegosource is a data visualization agent demo that uses the Anthropic Agent SDK to power a self-modifying Streamlit UI
- The agent modifies `app.py` directly, and Streamlit hot-reloads to show changes
- Mode: all-issues (autonomous workflow)

## Acceptance Criteria
- [ ] `agent.py` implements `ClaudeSDKClient` connection with streaming enabled
- [ ] System prompt defines the agent's role: it is Stegosource, a data visualization assistant that can modify the Streamlit app
- [ ] System prompt instructs the agent to preserve the scaffold section of `app.py` and only modify the dynamic section
- [ ] Agent has access to built-in tools: Read, Write, Edit, Bash
- [ ] Conversation history stored in a format suitable for replay across Streamlit reruns
- [ ] `asyncio.run()` bridges async SDK calls into Streamlit's sync execution model
- [ ] API key loaded from `.env` via `python-dotenv`
- [ ] Graceful error handling if `ANTHROPIC_API_KEY` is missing or invalid

## Technical Notes from Discovery

### Agent SDK API (claude-agent-sdk v0.1.36)

**Key classes and functions:**
- `ClaudeSDKClient(options: ClaudeAgentOptions)` - Bidirectional, stateful client for multi-turn conversations
- `query(prompt=..., options=...)` - One-shot stateless queries (simpler alternative)
- `ClaudeAgentOptions` - Configuration dataclass with fields:
  - `system_prompt: str | SystemPromptPreset | None` - Custom system prompt string
  - `tools: list[str] | ToolsPreset | None` - Tool list. Use `ToolsPreset(type="preset", preset="claude_code")` for built-in tools (Read, Write, Edit, Bash, etc.)
  - `permission_mode: Literal['default', 'acceptEdits', 'plan', 'bypassPermissions']` - Tool permission control
  - `include_partial_messages: bool` - Enable streaming partial messages
  - `cwd: str | Path | None` - Working directory for the agent
  - `model: str | None` - Model to use

**Streaming message types:**
- `SystemMessage` - System-level messages
- `AssistantMessage` - Contains `content: list[TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock]`
- `ResultMessage` - Final message with `is_error`, `total_cost_usd`, `session_id`, `result`
- `StreamEvent` - Partial streaming events (when `include_partial_messages=True`)
  - Has `event: dict[str, Any]` field with partial content

**Content block types:**
- `TextBlock` - Has `text: str`
- `ToolUseBlock` - Has `id: str`, `name: str`, `input: dict`
- `ToolResultBlock` - Has `tool_use_id: str`, `content: str | list[dict] | None`, `is_error: bool | None`

### Architecture Decision: Stateless per-rerun with history replay
- Each user message creates a new `query()` call with the full conversation history passed as context
- No persistent client across Streamlit reruns (Streamlit re-executes the whole script on each interaction)
- Use `asyncio.run()` to bridge async SDK calls into Streamlit's sync execution model
- Conversation history stored in `st.session_state` and replayed each turn
- This is the simplest approach appropriate for a demo

### System Prompt Design
The system prompt is critical - it needs to:
1. Define the agent as "Stegosource", a data visualization assistant
2. Explain the app.py structure: scaffold section (chat UI, agent connection) vs dynamic section (agent-modifiable)
3. Instruct the agent to NEVER modify the scaffold section
4. Tell the agent it can freely add/modify/remove Streamlit and Plotly code in the dynamic section
5. Note that Streamlit hot-reloads on file save

### Project Structure (existing)
```
stegosource/
├── app.py          # Streamlit app (currently minimal - will be expanded in issue #5)
├── agent.py        # Agent module (currently just loads dotenv - YOUR MAIN FILE)
├── tools/
│   └── __init__.py # Empty tools package
├── pyproject.toml  # Dependencies (claude-agent-sdk, streamlit, plotly, python-dotenv, requests)
└── .env.example    # Template: ANTHROPIC_API_KEY=your-key-here, ALPHAVANTAGE_API_KEY=your-key-here
```

### Current agent.py content
```python
"""Stegosource Agent Module.

Agent SDK client setup, tool definitions, and system prompt
for the self-modifying Streamlit UI agent.
"""

from dotenv import load_dotenv

load_dotenv()
```

### Current app.py content
```python
import streamlit as st

st.set_page_config(page_title="Stegosource", page_icon="🦕", layout="wide")

st.title("Stegosource")
st.write("Dynamic Data Visualization Agent with Self-Modifying UI")
```

## Implementation Guidance

### What to implement in agent.py:
1. **System prompt** as a module-level constant defining the agent's role and app.py structure rules
2. **`query_agent(user_message: str, conversation_history: list[dict]) -> AsyncIterator`** function that:
   - Creates `ClaudeAgentOptions` with system prompt, tools preset, permission mode, streaming enabled
   - Uses `claude_agent_sdk.query()` (stateless per-rerun approach) passing the conversation history + new message
   - Yields streaming messages (AssistantMessage, ResultMessage, StreamEvent) to the caller
3. **`run_agent_sync(user_message: str, conversation_history: list[dict]) -> list`** wrapper that:
   - Uses `asyncio.run()` to bridge async to sync for Streamlit
   - Collects all messages from the streaming iterator
   - Returns a list of messages for the caller to process
4. **Error handling**:
   - Check for `ANTHROPIC_API_KEY` environment variable, raise clear error if missing
   - Handle `ClaudeSDKError`, `CLIConnectionError`, `CLINotFoundError` from the SDK
   - Graceful fallback messages for any SDK errors

### Tools configuration:
- Use `ToolsPreset` typed dict: `{"type": "preset", "preset": "claude_code"}` to give the agent Read, Write, Edit, Bash tools
- Set `permission_mode="bypassPermissions"` since this is a demo with intentional full tool access
- Set `cwd` to the project directory so the agent can find and edit `app.py`

### Conversation history format:
- Store messages as a list of dicts with `role` ("user" or "assistant") and `content`
- For the query function, the conversation history needs to be part of the prompt context
- Since `query()` is stateless, include relevant context in the prompt itself

### What NOT to implement (out of scope for this issue):
- Chat UI in app.py (issue #3)
- Tool call display in UI (issue #4)
- App.py scaffold/dynamic section structure (issue #5)
- Alpha Vantage tool (issue #6)

## Expected Output
- Working `agent.py` with Agent SDK client, streaming support, system prompt
- Tests for the agent module (at minimum, test that options are configured correctly, system prompt is present)
- PR created with "Closes #2" in body
- All existing tests passing (`pytest`)
- Lint passing (`ruff check .`)

## Resources (Read as Needed)
- Issue details: `gh issue view 2`
- Agent SDK installed at: `/usr/local/python/3.12.1/lib/python3.12/site-packages/claude_agent_sdk/`
- Discovery doc: `discovery.md`
- Implementation plan: `implementation-plan.md`
- Project commands: `.claude/commands.md`
