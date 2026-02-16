"""Stegosource Agent Module.

Agent SDK client setup, tool definitions, and system prompt
for the self-modifying Streamlit UI agent.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from claude_agent_sdk import query
from claude_agent_sdk.types import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
)

load_dotenv()

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are **Stegosource**, a data visualization assistant that lives inside a \
Streamlit application. Your primary job is to help users explore and visualize \
data by **modifying the Streamlit app's source code in real time**.

## How the app works

The Streamlit app is in `app.py`. It has two clearly marked sections:

1. **Scaffold section** (between `# === SCAFFOLD START ===` and \
`# === SCAFFOLD END ===`): This contains the chat interface, agent \
connection, session state management, and imports. **You must NEVER modify \
anything inside the scaffold section.** Doing so will break the chat and \
crash the app.

2. **Dynamic section** (between `# === DYNAMIC START ===` and \
`# === DYNAMIC END ===`): This is YOUR workspace. You may freely add, \
modify, or remove any Streamlit or Plotly code here. When you save changes, \
Streamlit hot-reloads and the user immediately sees the updated UI.

## Rules

- **NEVER** edit code between the scaffold markers.
- **ALWAYS** place your generated code between the dynamic markers.
- Use `st.plotly_chart(fig, use_container_width=True)` for charts.
- Use `st.columns()`, `st.tabs()`, `st.expander()` for layout.
- Use `st.session_state` if you need persistent values across reruns.
- Write clean, well-commented Python so the user can learn from your code.
- If a request is unclear, ask a clarifying question before editing files.
- When fetching data, handle errors gracefully and inform the user.
- You have access to the following tools: Read, Write, Edit, Bash.
- The project root is the current working directory.
"""

# ---------------------------------------------------------------------------
# Conversation history helpers
# ---------------------------------------------------------------------------


def _build_prompt(
    user_message: str,
    conversation_history: list[dict[str, str]],
) -> str:
    """Build a prompt string from conversation history and new user message.

    Since we use the stateless ``query()`` helper, we replay the entire
    conversation as a formatted prompt so the agent retains context across
    Streamlit reruns.
    """
    parts: list[str] = []
    for msg in conversation_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            parts.append(f"[User]: {content}")
        else:
            parts.append(f"[Assistant]: {content}")

    parts.append(f"[User]: {user_message}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Agent options factory
# ---------------------------------------------------------------------------


def _make_options() -> ClaudeAgentOptions:
    """Create ``ClaudeAgentOptions`` configured for the Stegosource agent."""
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        tools={"type": "preset", "preset": "claude_code"},
        permission_mode="bypassPermissions",
        include_partial_messages=True,
        cwd=str(Path(__file__).resolve().parent),
        model="sonnet",
    )


# ---------------------------------------------------------------------------
# Core async query function
# ---------------------------------------------------------------------------

MessageType = AssistantMessage | ResultMessage | SystemMessage | StreamEvent


async def query_agent(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> list[MessageType]:
    """Send a message to the agent and collect all streaming responses.

    Parameters
    ----------
    user_message:
        The latest user message to send to the agent.
    conversation_history:
        Prior conversation turns as a list of ``{"role": ..., "content": ...}``
        dicts.  Defaults to an empty list.

    Returns
    -------
    list[MessageType]
        All messages received from the agent (AssistantMessage, ResultMessage,
        StreamEvent, etc.).

    Raises
    ------
    AgentConfigError
        If the ``ANTHROPIC_API_KEY`` environment variable is not set.
    AgentQueryError
        If the SDK raises an error during the query.
    """
    if conversation_history is None:
        conversation_history = []

    _validate_api_key()

    prompt = _build_prompt(user_message, conversation_history)
    options = _make_options()

    messages: list[MessageType] = []
    try:
        async for msg in query(prompt=prompt, options=options):
            messages.append(msg)
    except Exception as exc:  # noqa: BLE001
        raise AgentQueryError(str(exc)) from exc

    return messages


async def query_agent_streaming(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
):
    """Async generator that yields messages as they arrive from the agent.

    This is the streaming variant of :func:`query_agent`.  Use it when you
    want to display partial results in real time (e.g., progressive rendering
    in Streamlit).

    Yields
    ------
    MessageType
        Each message as it is received.
    """
    if conversation_history is None:
        conversation_history = []

    _validate_api_key()

    prompt = _build_prompt(user_message, conversation_history)
    options = _make_options()

    try:
        async for msg in query(prompt=prompt, options=options):
            yield msg
    except Exception as exc:  # noqa: BLE001
        raise AgentQueryError(str(exc)) from exc


# ---------------------------------------------------------------------------
# Synchronous wrapper for Streamlit
# ---------------------------------------------------------------------------


def run_agent_sync(
    user_message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> list[MessageType]:
    """Synchronous entry-point that bridges ``asyncio`` into Streamlit's
    synchronous execution model.

    Parameters
    ----------
    user_message:
        The latest user message.
    conversation_history:
        Prior conversation turns.

    Returns
    -------
    list[MessageType]
        All messages received from the agent.
    """
    return asyncio.run(query_agent(user_message, conversation_history))


# ---------------------------------------------------------------------------
# Message extraction helpers
# ---------------------------------------------------------------------------


def extract_assistant_text(messages: list[MessageType]) -> str:
    """Extract the concatenated assistant text from a list of messages.

    Iterates through all ``AssistantMessage`` objects and concatenates
    their ``TextBlock`` contents.
    """
    parts: list[str] = []
    for msg in messages:
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
    return "".join(parts)


def format_tool_label(tool_name: str, tool_input: dict[str, Any]) -> tuple[str, str]:
    """Generate a friendly label and Material icon for a tool call.

    Parameters
    ----------
    tool_name:
        The raw tool name from the SDK (e.g., "Edit", "Bash", "Read").
    tool_input:
        The tool's input parameters dict.

    Returns
    -------
    tuple[str, str]
        A ``(label, icon)`` pair.  The label is a human-friendly description
        like ``"Editing app.py"`` and the icon is a Streamlit Material icon
        string like ``":material/edit:"``.
    """
    path = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("filename")
        or ""
    )
    # Show only the basename for readability
    if path:
        path = path.rsplit("/", 1)[-1]

    if tool_name in ("Write", "Edit"):
        label = f"Editing {path}" if path else "Editing file"
        icon = ":material/edit:"
    elif tool_name == "Read":
        label = f"Reading {path}" if path else "Reading file"
        icon = ":material/description:"
    elif tool_name == "Bash":
        cmd = str(tool_input.get("command", tool_input.get("cmd", "")))
        # Truncate long commands
        summary = cmd[:60] + ("..." if len(cmd) > 60 else "")
        label = f"Running {summary}" if summary else "Running command"
        icon = ":material/terminal:"
    elif tool_name in ("WebFetch", "WebSearch"):
        label = "Fetching data"
        icon = ":material/public:"
    else:
        label = f"Using {tool_name}"
        icon = ":material/build:"

    return label, icon


_MAX_RESULT_LENGTH = 500
"""Maximum characters to include in a tool call result summary."""


def _truncate_result(result: Any) -> str:
    """Truncate a tool call result to a readable summary.

    Parameters
    ----------
    result:
        The raw result content from a ``ToolResultBlock``.

    Returns
    -------
    str
        A string representation, truncated to ``_MAX_RESULT_LENGTH`` characters.
    """
    if result is None:
        return ""
    text = str(result)
    if len(text) > _MAX_RESULT_LENGTH:
        remaining = len(text) - _MAX_RESULT_LENGTH
        return text[:_MAX_RESULT_LENGTH] + f"\n... ({remaining} more chars)"
    return text


def extract_tool_calls(
    messages: list[MessageType],
) -> list[dict[str, Any]]:
    """Extract tool use and result information from agent messages.

    Returns a list of dicts with keys ``name``, ``input``, ``result``,
    ``is_error``, ``label``, and ``icon`` for each tool call observed.
    """
    tool_uses: dict[str, dict[str, Any]] = {}

    for msg in messages:
        if not isinstance(msg, AssistantMessage):
            continue
        for block in msg.content:
            if isinstance(block, ToolUseBlock):
                label, icon = format_tool_label(block.name, block.input)
                tool_uses[block.id] = {
                    "name": block.name,
                    "input": block.input,
                    "result": None,
                    "is_error": False,
                    "label": label,
                    "icon": icon,
                }
            elif isinstance(block, ToolResultBlock):
                if block.tool_use_id in tool_uses:
                    tool_uses[block.tool_use_id]["result"] = block.content
                    tool_uses[block.tool_use_id]["is_error"] = block.is_error or False

    return list(tool_uses.values())


def extract_result(
    messages: list[MessageType],
) -> ResultMessage | None:
    """Return the ``ResultMessage`` from a list of messages, or ``None``."""
    for msg in messages:
        if isinstance(msg, ResultMessage):
            return msg
    return None


# ---------------------------------------------------------------------------
# Error classes
# ---------------------------------------------------------------------------


class AgentError(Exception):
    """Base exception for Stegosource agent errors."""


class AgentConfigError(AgentError):
    """Raised when required configuration is missing or invalid."""


class AgentQueryError(AgentError):
    """Raised when the Agent SDK query fails."""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _validate_api_key() -> None:
    """Raise ``AgentConfigError`` if ``ANTHROPIC_API_KEY`` is not set."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise AgentConfigError(
            "ANTHROPIC_API_KEY is not set. "
            "Please add it to your .env file or set it as an environment variable."
        )
