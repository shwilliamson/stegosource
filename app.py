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
    extract_assistant_text,
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
) -> tuple[str, list[MessageType]]:
    """Query the agent and stream the response, returning the full text and messages.

    This function bridges the async ``query_agent_streaming`` generator into
    Streamlit's synchronous execution model.  It collects all messages and
    extracts the concatenated assistant text.
    """
    all_messages: list[MessageType] = []

    async def _collect() -> None:
        async for msg in query_agent_streaming(prompt, history):
            all_messages.append(msg)

    loop = _get_or_create_event_loop()
    loop.run_until_complete(_collect())

    text = extract_assistant_text(all_messages)
    return text, all_messages


# ---------------------------------------------------------------------------
# Sidebar — chat interface
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("logo.jpeg", width=200)

    # Render existing chat history
    for msg in st.session_state.messages:
        avatar = "\N{SAUROPOD}" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

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

            try:
                full_text, _ = _stream_agent_response(user_prompt, conversation_history)
                if not full_text.strip():
                    full_text = "I processed your request."
                message_placeholder.markdown(full_text)
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
                {"role": "assistant", "content": full_text}
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
# === DYNAMIC END ===
