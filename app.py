"""Stegosource — Dynamic Data Visualization Agent with Self-Modifying UI.

This is the main Streamlit application. It has two clearly marked sections:

1. **Scaffold section** (SCAFFOLD START → SCAFFOLD END): Chat interface,
   session state, imports. The agent must NEVER modify this section.

2. **Dynamic section** (DYNAMIC START → DYNAMIC END): The agent's workspace.
   The agent freely adds charts, forms, and dashboards here. Streamlit
   hot-reloads when the file changes.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import streamlit as st

from agent import (
    AgentConfigError,
    AgentError,
    _truncate_result,
    extract_assistant_text,
    extract_tool_calls,
    query_agent_streaming,
)

if TYPE_CHECKING:
    from agent import MessageType

# === SCAFFOLD START === (Do NOT edit between scaffold markers)

st.set_page_config(page_title="Stegosource", page_icon="\N{SAUROPOD}", layout="wide")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ---------------------------------------------------------------------------
# Async-to-sync bridge for streaming
# ---------------------------------------------------------------------------


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Return the running event loop or create a new one.

    Streamlit runs synchronously, so we need a dedicated loop for the
    async streaming generator.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _stream_agent_response(
    prompt: str,
    history: list[dict[str, str]],
) -> tuple[str, list[MessageType], list[dict[str, object]]]:
    """Query the agent and stream the response, returning text, messages, and tool calls.

    This function bridges the async ``query_agent_streaming`` generator into
    Streamlit's synchronous execution model.  It collects all messages,
    extracts the concatenated assistant text, and extracts tool call data.

    Returns
    -------
    tuple[str, list[MessageType], list[dict[str, object]]]
        A tuple of ``(assistant_text, raw_messages, tool_calls)``.
    """
    all_messages: list[MessageType] = []

    async def _collect() -> None:
        async for msg in query_agent_streaming(prompt, history):
            all_messages.append(msg)

    loop = _get_or_create_event_loop()
    loop.run_until_complete(_collect())

    text = extract_assistant_text(all_messages)
    tool_calls = extract_tool_calls(all_messages)
    return text, all_messages, tool_calls


def _render_tool_calls(tool_calls: list[dict[str, object]]) -> None:
    """Render tool calls as expanders within the current chat message context.

    Each tool call is displayed as a collapsed ``st.expander`` with the
    friendly label and Material icon.  The expanded content shows key
    parameters and a truncated result summary.
    """
    for tc in tool_calls:
        label = str(tc.get("label", tc.get("name", "Tool call")))
        icon = str(tc.get("icon", ":material/build:"))
        is_error = bool(tc.get("is_error", False))

        if is_error:
            label = f"Failed: {label}"

        with st.expander(label, expanded=False, icon=icon):
            # Show key input parameters
            tool_input = tc.get("input")
            if tool_input and isinstance(tool_input, dict):
                # Show a compact representation of key parameters
                params = {k: v for k, v in tool_input.items() if v is not None}
                if params:
                    st.caption("Parameters")
                    st.code(
                        "\n".join(f"{k}: {v}" for k, v in params.items()),
                        language="yaml",
                    )

            # Show result summary
            result = tc.get("result")
            if result is not None:
                st.caption("Result")
                result_text = _truncate_result(result)
                st.code(result_text, language="text")


# ---------------------------------------------------------------------------
# Sidebar — chat interface
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("logo.jpeg", use_container_width=False)
    st.markdown("### Stegosource")
    st.caption("Dynamic Data Visualization Agent")
    st.divider()

    # Render existing chat history
    for msg in st.session_state.messages:
        avatar = "\N{SAUROPOD}" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            # Render tool calls for assistant messages (if any)
            if msg["role"] == "assistant" and msg.get("tool_calls"):
                _render_tool_calls(msg["tool_calls"])

    # Handle streaming response if processing
    if st.session_state.processing and st.session_state.pending_prompt is not None:
        user_prompt: str = st.session_state.pending_prompt
        conversation_history: list[dict[str, str]] = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]  # exclude the just-added user msg
        ]

        with st.chat_message("assistant", avatar="\N{SAUROPOD}"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking\u2026")
            tool_calls_data: list[dict[str, object]] = []

            try:
                full_text, _, tool_calls_data = _stream_agent_response(
                    user_prompt, conversation_history
                )
                if not full_text.strip():
                    full_text = "I processed your request."
                message_placeholder.markdown(full_text)
                # Render tool calls inline after the text
                if tool_calls_data:
                    _render_tool_calls(tool_calls_data)
            except AgentConfigError:
                full_text = ""
                message_placeholder.empty()
                st.error(
                    "ANTHROPIC_API_KEY is not set. "
                    "Please add it to your .env file and restart the app."
                )
            except AgentError as exc:
                full_text = ""
                message_placeholder.empty()
                st.error(f"Something went wrong: {exc}")
            except Exception:  # noqa: BLE001
                full_text = ""
                message_placeholder.empty()
                st.error("An unexpected error occurred. Please try again.")

        if full_text:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_text,
                    "tool_calls": tool_calls_data,
                }
            )

        st.session_state.processing = False
        st.session_state.pending_prompt = None
        st.rerun()

    # Chat input — always rendered so Streamlit keeps it pinned at the bottom
    if prompt := st.chat_input(
        "Ask Stegosource\u2026",
        disabled=st.session_state.processing,
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.processing = True
        st.session_state.pending_prompt = prompt
        st.rerun()

# === SCAFFOLD END ===

# === DYNAMIC START ===
# Agent-generated UI goes here. The agent may freely add, modify, or remove
# any Streamlit or Plotly code in this section.

# ---------------------------------------------------------------------------
# Default empty state — shown until the agent modifies this section
# ---------------------------------------------------------------------------

EXAMPLE_PROMPTS: list[str] = [
    "Show me AAPL stock for the last 3 months",
    "Add a date range picker",
    "Compare TSLA and F",
    "Create a candlestick chart for GOOGL",
]


def _send_example_prompt(prompt_text: str) -> None:
    """Callback for example prompt buttons.

    Populates the chat with the selected prompt and triggers processing.
    """
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.session_state.processing = True
    st.session_state.pending_prompt = prompt_text


# Centre the empty state content in the main area
_left_spacer, _center_col, _right_spacer = st.columns([1, 2, 1])

with _center_col:
    st.image("logo.jpeg", use_container_width=False)
    st.caption("Dynamic Data Visualization Agent")
    st.write(
        "Ask Stegosource to fetch financial data, build interactive charts, "
        "and create dashboards — all through natural conversation."
    )

    st.divider()

    # 2x2 grid of example prompt cards
    _row1_left, _row1_right = st.columns(2)
    _row2_left, _row2_right = st.columns(2)

    with _row1_left:
        st.button(
            EXAMPLE_PROMPTS[0],
            key="example_prompt_0",
            use_container_width=True,
            on_click=_send_example_prompt,
            args=(EXAMPLE_PROMPTS[0],),
        )
    with _row1_right:
        st.button(
            EXAMPLE_PROMPTS[1],
            key="example_prompt_1",
            use_container_width=True,
            on_click=_send_example_prompt,
            args=(EXAMPLE_PROMPTS[1],),
        )
    with _row2_left:
        st.button(
            EXAMPLE_PROMPTS[2],
            key="example_prompt_2",
            use_container_width=True,
            on_click=_send_example_prompt,
            args=(EXAMPLE_PROMPTS[2],),
        )
    with _row2_right:
        st.button(
            EXAMPLE_PROMPTS[3],
            key="example_prompt_3",
            use_container_width=True,
            on_click=_send_example_prompt,
            args=(EXAMPLE_PROMPTS[3],),
        )

# === DYNAMIC END ===
