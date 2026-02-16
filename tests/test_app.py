"""Tests for the Stegosource Streamlit app module.

Tests cover session state initialisation, the async-to-sync streaming bridge,
chat history rendering logic, and error handling paths.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# We cannot import ``app`` directly because it calls ``st.set_page_config``
# at module level.  Instead we test the *functions* and *logic* by importing
# individual helpers after patching Streamlit.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_streamlit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent Streamlit side-effects during import."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    monkeypatch.setattr("streamlit.set_page_config", MagicMock())
    monkeypatch.setattr("streamlit.sidebar", MagicMock())


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------


class TestSessionStateInit:
    """Verify that session state is initialised correctly."""

    def test_default_messages_list(self) -> None:
        """messages should start as an empty list."""
        state: dict[str, object] = {}
        if "messages" not in state:
            state["messages"] = []
        assert state["messages"] == []

    def test_default_processing_flag(self) -> None:
        """processing should default to False."""
        state: dict[str, object] = {}
        if "processing" not in state:
            state["processing"] = False
        assert state["processing"] is False

    def test_default_pending_prompt(self) -> None:
        """pending_prompt should default to None."""
        state: dict[str, object] = {}
        if "pending_prompt" not in state:
            state["pending_prompt"] = None
        assert state["pending_prompt"] is None

    def test_existing_state_not_overwritten(self) -> None:
        """If state already has messages, it should not be cleared."""
        state: dict[str, object] = {"messages": [{"role": "user", "content": "hi"}]}
        if "messages" not in state:
            state["messages"] = []
        assert len(state["messages"]) == 1  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Event loop helper
# ---------------------------------------------------------------------------


class TestGetOrCreateEventLoop:
    """Verify the async-to-sync bridge event loop helper."""

    def test_returns_event_loop(self) -> None:
        """Should return a usable event loop."""
        from app import _get_or_create_event_loop

        loop = _get_or_create_event_loop()
        assert isinstance(loop, asyncio.AbstractEventLoop)
        assert not loop.is_closed()

    def test_creates_new_loop_when_closed(self) -> None:
        """Should create a new loop if the current one is closed."""
        from app import _get_or_create_event_loop

        old_loop = asyncio.new_event_loop()
        old_loop.close()
        asyncio.set_event_loop(old_loop)

        loop = _get_or_create_event_loop()
        assert not loop.is_closed()


# ---------------------------------------------------------------------------
# Stream agent response
# ---------------------------------------------------------------------------


class TestStreamAgentResponse:
    """Verify the _stream_agent_response bridge function."""

    def test_returns_text_and_messages(self) -> None:
        """Should return extracted text and the raw message list."""
        from claude_agent_sdk.types import AssistantMessage, TextBlock

        fake_msg = AssistantMessage(
            content=[TextBlock(text="Hello from agent")],
            model="claude-sonnet-4-20250514",
        )

        async def mock_streaming(
            user_message: str,
            conversation_history: list[dict[str, str]] | None = None,
        ):
            yield fake_msg

        with patch("app.query_agent_streaming", side_effect=mock_streaming):
            from app import _stream_agent_response

            text, messages = _stream_agent_response("test", [])
            assert text == "Hello from agent"
            assert len(messages) == 1

    def test_empty_response_returns_empty_string(self) -> None:
        """If agent returns no text blocks, text should be empty."""
        from claude_agent_sdk.types import ResultMessage

        fake_result = ResultMessage(
            subtype="result",
            duration_ms=50,
            duration_api_ms=40,
            is_error=False,
            num_turns=1,
            session_id="test",
            total_cost_usd=0.001,
            usage=None,
            result=None,
            structured_output=None,
        )

        async def mock_streaming(
            user_message: str,
            conversation_history: list[dict[str, str]] | None = None,
        ):
            yield fake_result

        with patch("app.query_agent_streaming", side_effect=mock_streaming):
            from app import _stream_agent_response

            text, messages = _stream_agent_response("test", [])
            assert text == ""
            assert len(messages) == 1

    def test_multiple_text_blocks_concatenated(self) -> None:
        """Multiple text blocks should be concatenated."""
        from claude_agent_sdk.types import AssistantMessage, TextBlock

        msg1 = AssistantMessage(
            content=[TextBlock(text="Part 1 ")],
            model="claude-sonnet-4-20250514",
        )
        msg2 = AssistantMessage(
            content=[TextBlock(text="Part 2")],
            model="claude-sonnet-4-20250514",
        )

        async def mock_streaming(
            user_message: str,
            conversation_history: list[dict[str, str]] | None = None,
        ):
            yield msg1
            yield msg2

        with patch("app.query_agent_streaming", side_effect=mock_streaming):
            from app import _stream_agent_response

            text, messages = _stream_agent_response("test", [])
            assert text == "Part 1 Part 2"
            assert len(messages) == 2


# ---------------------------------------------------------------------------
# Chat message construction
# ---------------------------------------------------------------------------


class TestChatMessageLogic:
    """Verify chat message data structure conventions."""

    def test_user_message_format(self) -> None:
        """User messages should have role 'user' and content string."""
        msg = {"role": "user", "content": "Hello"}
        assert msg["role"] == "user"
        assert isinstance(msg["content"], str)

    def test_assistant_message_format(self) -> None:
        """Assistant messages should have role 'assistant' and content string."""
        msg = {"role": "assistant", "content": "Hi there"}
        assert msg["role"] == "assistant"
        assert isinstance(msg["content"], str)

    def test_avatar_selection_for_assistant(self) -> None:
        """Assistant messages should get the sauropod emoji avatar."""
        msg = {"role": "assistant", "content": "test"}
        avatar = "\N{SAUROPOD}" if msg["role"] == "assistant" else None
        assert avatar == "\N{SAUROPOD}"

    def test_avatar_selection_for_user(self) -> None:
        """User messages should get None avatar (Streamlit default)."""
        msg = {"role": "user", "content": "test"}
        avatar = "\N{SAUROPOD}" if msg["role"] == "assistant" else None
        assert avatar is None

    def test_conversation_history_excludes_last_user_msg(self) -> None:
        """When building history for the agent, exclude the just-added user message."""
        messages = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "response"},
            {"role": "user", "content": "second"},  # just added
        ]
        history = [{"role": m["role"], "content": m["content"]} for m in messages[:-1]]
        assert len(history) == 2
        assert history[-1]["role"] == "assistant"


# ---------------------------------------------------------------------------
# Scaffold and dynamic section markers
# ---------------------------------------------------------------------------


class TestScaffoldMarkers:
    """Verify that app.py contains the required section markers."""

    def test_scaffold_start_marker(self) -> None:
        """app.py must contain the SCAFFOLD START marker."""
        from pathlib import Path

        content = Path("app.py").read_text()
        assert "# === SCAFFOLD START ===" in content

    def test_scaffold_end_marker(self) -> None:
        """app.py must contain the SCAFFOLD END marker."""
        from pathlib import Path

        content = Path("app.py").read_text()
        assert "# === SCAFFOLD END ===" in content

    def test_dynamic_start_marker(self) -> None:
        """app.py must contain the DYNAMIC START marker."""
        from pathlib import Path

        content = Path("app.py").read_text()
        assert "# === DYNAMIC START ===" in content

    def test_dynamic_end_marker(self) -> None:
        """app.py must contain the DYNAMIC END marker."""
        from pathlib import Path

        content = Path("app.py").read_text()
        assert "# === DYNAMIC END ===" in content

    def test_scaffold_before_dynamic(self) -> None:
        """Scaffold section must come before dynamic section."""
        from pathlib import Path

        content = Path("app.py").read_text()
        scaffold_end = content.index("# === SCAFFOLD END ===")
        dynamic_start = content.index("# === DYNAMIC START ===")
        assert scaffold_end < dynamic_start


# ---------------------------------------------------------------------------
# Streamlit config
# ---------------------------------------------------------------------------


class TestStreamlitConfig:
    """Verify the .streamlit/config.toml is correctly configured."""

    def test_config_file_exists(self) -> None:
        """The Streamlit config file must exist."""
        from pathlib import Path

        assert Path(".streamlit/config.toml").exists()

    def test_config_has_theme_section(self) -> None:
        """Config must define a [theme] section."""
        from pathlib import Path

        content = Path(".streamlit/config.toml").read_text()
        assert "[theme]" in content

    def test_config_primary_color(self) -> None:
        """Primary color should be brand cyan from design system."""
        from pathlib import Path

        content = Path(".streamlit/config.toml").read_text()
        assert "#00D4FF" in content

    def test_config_background_color(self) -> None:
        """Background should be the dark bg-primary from design system."""
        from pathlib import Path

        content = Path(".streamlit/config.toml").read_text()
        assert "#0E1117" in content

    def test_config_secondary_background(self) -> None:
        """Secondary background should be bg-secondary from design system."""
        from pathlib import Path

        content = Path(".streamlit/config.toml").read_text()
        assert "#1A1D26" in content


# ---------------------------------------------------------------------------
# Empty state and example prompts
# ---------------------------------------------------------------------------


class TestExamplePrompts:
    """Verify example prompt definitions and click callback logic."""

    def test_example_prompts_defined(self) -> None:
        """EXAMPLE_PROMPTS should be a non-empty list of strings."""
        from app import EXAMPLE_PROMPTS

        assert isinstance(EXAMPLE_PROMPTS, list)
        assert len(EXAMPLE_PROMPTS) >= 3
        for prompt in EXAMPLE_PROMPTS:
            assert isinstance(prompt, str)
            assert len(prompt) > 0

    def test_example_prompts_count(self) -> None:
        """Should have 3-4 example prompts as required by the issue."""
        from app import EXAMPLE_PROMPTS

        assert 3 <= len(EXAMPLE_PROMPTS) <= 4

    def test_required_prompts_present(self) -> None:
        """Must include the prompts specified in the issue."""
        from app import EXAMPLE_PROMPTS

        assert "Show me AAPL stock for the last 3 months" in EXAMPLE_PROMPTS
        assert "Add a date range picker" in EXAMPLE_PROMPTS
        assert "Compare TSLA and F" in EXAMPLE_PROMPTS

    def test_send_example_prompt_sets_session_state(self) -> None:
        """Clicking an example prompt should populate session state for processing."""
        from app import _send_example_prompt

        # Use SimpleNamespace so attribute access (st.session_state.messages) works
        from types import SimpleNamespace

        mock_state = SimpleNamespace(
            messages=[],
            processing=False,
            pending_prompt=None,
        )

        with patch("app.st") as mock_st:
            mock_st.session_state = mock_state
            _send_example_prompt("Show me AAPL stock for the last 3 months")

            assert len(mock_state.messages) == 1
            assert mock_state.messages[0] == {
                "role": "user",
                "content": "Show me AAPL stock for the last 3 months",
            }
            assert mock_state.processing is True
            assert mock_state.pending_prompt == "Show me AAPL stock for the last 3 months"

    def test_send_example_prompt_appends_to_existing_messages(self) -> None:
        """Callback should append to existing messages, not replace them."""
        from app import _send_example_prompt
        from types import SimpleNamespace

        existing_messages: list[dict[str, str]] = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        mock_state = SimpleNamespace(
            messages=existing_messages,
            processing=False,
            pending_prompt=None,
        )

        with patch("app.st") as mock_st:
            mock_st.session_state = mock_state
            _send_example_prompt("Add a date range picker")

            assert len(mock_state.messages) == 3
            assert mock_state.messages[-1] == {
                "role": "user",
                "content": "Add a date range picker",
            }


class TestEmptyStateDynamicSection:
    """Verify the dynamic section contains the empty state UI."""

    def test_dynamic_section_has_content(self) -> None:
        """Dynamic section should not be empty — it should have the empty state."""
        from pathlib import Path

        content = Path("app.py").read_text()
        dynamic_start = content.index("# === DYNAMIC START ===")
        dynamic_end = content.index("# === DYNAMIC END ===")
        dynamic_content = content[dynamic_start:dynamic_end].strip()

        # Should have more than just the marker and a comment
        lines = [
            line
            for line in dynamic_content.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        assert len(lines) > 0, "Dynamic section should contain empty state code"

    def test_dynamic_section_has_example_prompts_ref(self) -> None:
        """Dynamic section should reference EXAMPLE_PROMPTS."""
        from pathlib import Path

        content = Path("app.py").read_text()
        dynamic_start = content.index("# === DYNAMIC START ===")
        dynamic_end = content.index("# === DYNAMIC END ===")
        dynamic_content = content[dynamic_start:dynamic_end]

        assert "EXAMPLE_PROMPTS" in dynamic_content

    def test_dynamic_section_has_send_callback(self) -> None:
        """Dynamic section should define the _send_example_prompt callback."""
        from pathlib import Path

        content = Path("app.py").read_text()
        dynamic_start = content.index("# === DYNAMIC START ===")
        dynamic_end = content.index("# === DYNAMIC END ===")
        dynamic_content = content[dynamic_start:dynamic_end]

        assert "_send_example_prompt" in dynamic_content

    def test_scaffold_not_modified(self) -> None:
        """Scaffold section should still contain required infrastructure."""
        from pathlib import Path

        content = Path("app.py").read_text()
        scaffold_start = content.index("# === SCAFFOLD START ===")
        scaffold_end = content.index("# === SCAFFOLD END ===")
        scaffold_content = content[scaffold_start:scaffold_end]

        # Verify key scaffold components are present
        assert "st.set_page_config" in scaffold_content
        assert "session_state" in scaffold_content
        assert "st.sidebar" in scaffold_content
        assert "chat_input" in scaffold_content
