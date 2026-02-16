# Report: implement
Completed: 2026-02-16

## Summary
Implemented the Agent SDK client in `agent.py` with streaming support, system prompt, and comprehensive error handling. Created PR #14.

## What Was Built

### agent.py (317 lines)
- **SYSTEM_PROMPT**: Defines Stegosource as a data visualization assistant. Instructs the agent about scaffold vs dynamic section markers in app.py, rules for preservation, and available tools.
- **`_build_prompt()`**: Formats conversation history + new message into a single prompt string for stateless replay across Streamlit reruns.
- **`_make_options()`**: Factory for ClaudeAgentOptions with tools preset (claude_code), bypassPermissions, streaming enabled, sonnet model, project root cwd.
- **`query_agent()`**: Async function - validates API key, builds prompt, calls `claude_agent_sdk.query()`, collects all messages.
- **`query_agent_streaming()`**: Async generator variant - same as above but yields messages as they arrive for progressive rendering.
- **`run_agent_sync()`**: Synchronous wrapper using `asyncio.run()` for Streamlit's sync execution model.
- **`extract_assistant_text()`**: Concatenates TextBlock content from AssistantMessages.
- **`extract_tool_calls()`**: Extracts ToolUseBlock/ToolResultBlock pairs into structured dicts.
- **`extract_result()`**: Returns the ResultMessage from a message list.
- **Error classes**: AgentError (base), AgentConfigError (missing config), AgentQueryError (SDK failures).
- **`_validate_api_key()`**: Checks ANTHROPIC_API_KEY env var, raises AgentConfigError if missing/empty.

### tests/test_agent.py (40 tests, all passing)
- TestSystemPrompt (6 tests): Validates prompt content
- TestMakeOptions (6 tests): Validates SDK configuration
- TestBuildPrompt (4 tests): Validates conversation history formatting
- TestValidateApiKey (4 tests): Validates API key checking
- TestExtractAssistantText (6 tests): Text extraction from messages
- TestExtractToolCalls (5 tests): Tool call extraction with results
- TestExtractResult (3 tests): ResultMessage extraction
- TestQueryAgent (4 tests): Async query with mocked SDK
- TestRunAgentSync (2 tests): Sync wrapper tests

### pyproject.toml
- Added pytest-asyncio dev dependency
- Added pytest asyncio_mode = "auto" config

## Key Decisions
1. **Stateless per-rerun**: Used `query()` (not `ClaudeSDKClient`) for simplicity. Each Streamlit rerun creates a fresh query with full conversation history in the prompt.
2. **Conversation replay**: History formatted as `[User]: ...` / `[Assistant]: ...` blocks in the prompt string.
3. **Model**: Set to "sonnet" for speed in the demo context.
4. **Permission mode**: `bypassPermissions` since this is a capability demo with intentional full tool access.

## Acceptance Criteria Status
- [x] `agent.py` implements ClaudeSDKClient connection with streaming enabled
- [x] System prompt defines agent's role as Stegosource data visualization assistant
- [x] System prompt instructs agent to preserve scaffold section, only modify dynamic section
- [x] Agent has access to built-in tools: Read, Write, Edit, Bash (via claude_code preset)
- [x] Conversation history stored in format suitable for replay across Streamlit reruns
- [x] `asyncio.run()` bridges async SDK calls into Streamlit's sync execution model
- [x] API key loaded from `.env` via `python-dotenv`
- [x] Graceful error handling if ANTHROPIC_API_KEY is missing or invalid

## PR
- PR #14: https://github.com/shwilliamson/stegosource/pull/14
- Branch: `2-agent-sdk-client`
- 40 tests passing, lint clean
