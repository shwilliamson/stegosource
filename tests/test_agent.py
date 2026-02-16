"""Tests for the Stegosource agent module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agent import (
    SYSTEM_PROMPT,
    AgentConfigError,
    AgentQueryError,
    _build_prompt,
    _make_options,
    _truncate_result,
    _validate_api_key,
    extract_assistant_text,
    extract_result,
    extract_tool_calls,
    format_tool_label,
    query_agent,
    run_agent_sync,
)
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
)


# ---------------------------------------------------------------------------
# System prompt tests
# ---------------------------------------------------------------------------


class TestSystemPrompt:
    """Verify the system prompt contains required instructions."""

    def test_defines_agent_role(self) -> None:
        assert "Stegosource" in SYSTEM_PROMPT
        assert "data visualization" in SYSTEM_PROMPT.lower()

    def test_instructs_scaffold_preservation(self) -> None:
        assert "SCAFFOLD START" in SYSTEM_PROMPT
        assert "SCAFFOLD END" in SYSTEM_PROMPT
        assert "NEVER modify" in SYSTEM_PROMPT or "NEVER edit" in SYSTEM_PROMPT

    def test_defines_dynamic_section(self) -> None:
        assert "DYNAMIC START" in SYSTEM_PROMPT
        assert "DYNAMIC END" in SYSTEM_PROMPT

    def test_mentions_available_tools(self) -> None:
        for tool in ("Read", "Write", "Edit", "Bash"):
            assert tool in SYSTEM_PROMPT

    def test_mentions_plotly(self) -> None:
        assert "plotly_chart" in SYSTEM_PROMPT

    def test_mentions_hot_reload(self) -> None:
        assert (
            "hot-reload" in SYSTEM_PROMPT.lower()
            or "hot reload" in SYSTEM_PROMPT.lower()
        )

    def test_contains_chart_generation_section(self) -> None:
        """System prompt must include chart generation patterns."""
        assert "Chart Generation Patterns" in SYSTEM_PROMPT

    def test_contains_line_chart_example(self) -> None:
        """System prompt must include a line chart example with px.line."""
        assert "px.line" in SYSTEM_PROMPT

    def test_contains_candlestick_chart_example(self) -> None:
        """System prompt must include a candlestick chart example."""
        assert "go.Candlestick" in SYSTEM_PROMPT

    def test_contains_stego_layout_reference(self) -> None:
        """System prompt must reference the STEGO_LAYOUT theme template."""
        assert "STEGO_LAYOUT" in SYSTEM_PROMPT

    def test_contains_chart_theme_import(self) -> None:
        """System prompt must show how to import from chart_theme module."""
        assert "from chart_theme import" in SYSTEM_PROMPT

    def test_contains_alpha_vantage_import_pattern(self) -> None:
        """System prompt must show inline import of fetch_daily."""
        assert "from tools.alpha_vantage import fetch_daily" in SYSTEM_PROMPT

    def test_contains_error_handling_pattern(self) -> None:
        """System prompt chart examples must include try/except error handling."""
        assert "except InvalidTickerError" in SYSTEM_PROMPT
        assert "except RateLimitError" in SYSTEM_PROMPT
        assert "st.error" in SYSTEM_PROMPT

    def test_contains_chart_title_guidance(self) -> None:
        """System prompt must mention chart titles."""
        assert "title=" in SYSTEM_PROMPT

    def test_contains_axis_label_guidance(self) -> None:
        """System prompt must mention axis labels."""
        assert "xaxis_title" in SYSTEM_PROMPT or "labels=" in SYSTEM_PROMPT

    def test_contains_caption_pattern(self) -> None:
        """System prompt must include st.caption for data source attribution."""
        assert "st.caption" in SYSTEM_PROMPT

    def test_contains_candlestick_colors(self) -> None:
        """System prompt must reference candlestick up/down colors."""
        assert "CANDLESTICK_UP" in SYSTEM_PROMPT
        assert "CANDLESTICK_DOWN" in SYSTEM_PROMPT

    def test_contains_error_handling_section(self) -> None:
        """System prompt must include a dedicated Error Handling section."""
        assert "## Error Handling" in SYSTEM_PROMPT

    def test_contains_invalid_ticker_guidance(self) -> None:
        """System prompt must instruct agent on InvalidTickerError handling."""
        assert "InvalidTickerError" in SYSTEM_PROMPT
        assert "Did you mean" in SYSTEM_PROMPT

    def test_contains_rate_limit_toast_guidance(self) -> None:
        """System prompt must instruct use of st.toast for rate limits."""
        assert "st.toast" in SYSTEM_PROMPT
        assert "rate limit" in SYSTEM_PROMPT.lower()

    def test_contains_missing_api_key_guidance(self) -> None:
        """System prompt must instruct on MissingApiKeyError handling."""
        assert "MissingApiKeyError" in SYSTEM_PROMPT
        assert "st.warning" in SYSTEM_PROMPT

    def test_contains_network_error_guidance(self) -> None:
        """System prompt must instruct on ApiError (network) handling."""
        assert "ApiError" in SYSTEM_PROMPT
        assert "network" in SYSTEM_PROMPT.lower()

    def test_contains_code_quality_section(self) -> None:
        """System prompt must include code quality checklist."""
        assert "Code Quality" in SYSTEM_PROMPT
        assert "Mentally trace" in SYSTEM_PROMPT

    def test_contains_error_recovery_section(self) -> None:
        """System prompt must include an Error Recovery section."""
        assert "Error Recovery" in SYSTEM_PROMPT

    def test_error_recovery_mentions_try_except(self) -> None:
        """Error recovery section should mention the try/except wrapper."""
        assert "try/except" in SYSTEM_PROMPT or "try block" in SYSTEM_PROMPT

    def test_error_recovery_mentions_traceback(self) -> None:
        """Error recovery should instruct agent to read the traceback."""
        assert "traceback" in SYSTEM_PROMPT.lower()

    def test_error_recovery_mentions_read_app(self) -> None:
        """Error recovery should instruct agent to read app.py before editing."""
        recovery_start = SYSTEM_PROMPT.index("Error Recovery")
        recovery_section = SYSTEM_PROMPT[recovery_start:]
        assert "Read" in recovery_section
        assert "app.py" in recovery_section

    def test_error_recovery_mentions_reset_button(self) -> None:
        """Error recovery should mention the Reset Workspace button."""
        assert "Reset Workspace" in SYSTEM_PROMPT

    def test_error_recovery_mentions_chat_still_works(self) -> None:
        """Error recovery should note that chat remains functional during errors."""
        recovery_start = SYSTEM_PROMPT.index("Error Recovery")
        recovery_section = SYSTEM_PROMPT[recovery_start:]
        assert (
            "chat" in recovery_section.lower() or "sidebar" in recovery_section.lower()
        )

    def test_code_quality_instructs_read_before_edit(self) -> None:
        """Code quality section should instruct reading app.py before editing."""
        quality_start = SYSTEM_PROMPT.index("Code Quality")
        quality_end = SYSTEM_PROMPT.index("Error Recovery")
        quality_section = SYSTEM_PROMPT[quality_start:quality_end]
        assert "Read" in quality_section
        assert "app.py" in quality_section

    def test_contains_specific_exception_imports(self) -> None:
        """System prompt error handling pattern must import specific exceptions."""
        assert "from tools.alpha_vantage import" in SYSTEM_PROMPT
        assert "InvalidTickerError" in SYSTEM_PROMPT
        assert "RateLimitError" in SYSTEM_PROMPT
        assert "MissingApiKeyError" in SYSTEM_PROMPT

    def test_contains_multi_symbol_example(self) -> None:
        """System prompt must include a multi-symbol comparison example."""
        assert "Multi-Symbol Comparison" in SYSTEM_PROMPT
        assert "add_trace" in SYSTEM_PROMPT

    def test_contains_modify_chart_guidance(self) -> None:
        """System prompt must include guidance on modifying existing charts."""
        assert "Modifying Existing Charts" in SYSTEM_PROMPT

    def test_contains_chart_checklist(self) -> None:
        """System prompt must include a pre-save chart checklist."""
        assert "Chart Checklist" in SYSTEM_PROMPT
        assert 'width="stretch"' in SYSTEM_PROMPT

    # --- Form and Widget Generation Tests ---

    def test_contains_form_widget_section(self) -> None:
        """System prompt must include a Form and Widget Generation section."""
        assert "Form and Widget Generation Patterns" in SYSTEM_PROMPT

    def test_contains_widget_key_guidance(self) -> None:
        """System prompt must instruct use of key parameters for widgets."""
        assert "key=" in SYSTEM_PROMPT
        assert "session state persistence" in SYSTEM_PROMPT.lower()

    def test_contains_date_range_picker_example(self) -> None:
        """System prompt must include a date range picker example."""
        assert "Date Range Picker" in SYSTEM_PROMPT
        assert "st.date_input" in SYSTEM_PROMPT
        assert "date_start" in SYSTEM_PROMPT

    def test_contains_dropdown_selector_example(self) -> None:
        """System prompt must include a dropdown selector example."""
        assert "Dropdown Selector" in SYSTEM_PROMPT
        assert "st.selectbox" in SYSTEM_PROMPT
        assert "chart_type_selector" in SYSTEM_PROMPT

    def test_contains_text_input_example(self) -> None:
        """System prompt must include a text input example."""
        assert "Text Input" in SYSTEM_PROMPT
        assert "st.text_input" in SYSTEM_PROMPT
        assert "symbol_input" in SYSTEM_PROMPT

    def test_contains_multiselect_example(self) -> None:
        """System prompt must include a multi-select example."""
        assert "Multi-Select" in SYSTEM_PROMPT
        assert "st.multiselect" in SYSTEM_PROMPT
        assert "compare_symbols" in SYSTEM_PROMPT

    def test_contains_form_submit_pattern(self) -> None:
        """System prompt must include st.form with st.form_submit_button pattern."""
        assert "st.form(" in SYSTEM_PROMPT
        assert "st.form_submit_button" in SYSTEM_PROMPT
        assert "stock_form" in SYSTEM_PROMPT or "form_symbol" in SYSTEM_PROMPT

    def test_contains_widget_modify_remove_guidance(self) -> None:
        """System prompt must include guidance on modifying/removing controls."""
        assert "Modifying or Removing Controls" in SYSTEM_PROMPT

    def test_contains_widget_checklist(self) -> None:
        """System prompt must include a widget checklist."""
        assert "Widget Checklist" in SYSTEM_PROMPT
        assert "unique `key` parameter" in SYSTEM_PROMPT

    def test_widget_examples_use_error_handling(self) -> None:
        """Widget examples must include error handling with specific exceptions."""
        # The form section should contain try/except patterns
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "except InvalidTickerError" in form_section
        assert "except RateLimitError" in form_section
        assert "except MissingApiKeyError" in form_section
        assert "except ApiError" in form_section

    def test_widget_examples_use_chart_theme(self) -> None:
        """Widget examples must apply STEGO_LAYOUT for chart theming."""
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "STEGO_LAYOUT" in form_section

    def test_widget_examples_use_alpha_vantage(self) -> None:
        """Widget examples must use fetch_daily from alpha_vantage."""
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "fetch_daily" in form_section

    def test_widget_examples_connect_to_charts(self) -> None:
        """Widget examples must show widgets driving chart updates."""
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "st.plotly_chart" in form_section

    def test_form_example_has_columns_layout(self) -> None:
        """Form examples should use st.columns for side-by-side widget layout."""
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "st.columns" in form_section

    def test_widget_rerun_guidance(self) -> None:
        """System prompt must mention Streamlit rerun behaviour for widgets."""
        form_section_start = SYSTEM_PROMPT.index("Form and Widget Generation")
        form_section = SYSTEM_PROMPT[form_section_start:]
        assert "rerun" in form_section.lower()

    # --- Complex Layout Patterns Tests ---

    def test_contains_complex_layout_section(self) -> None:
        """System prompt must include a Complex Layout Patterns section."""
        assert "Complex Layout Patterns" in SYSTEM_PROMPT

    def test_contains_columns_guidance(self) -> None:
        """System prompt must document st.columns() for side-by-side layouts."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "st.columns()" in layout_section

    def test_contains_tabs_guidance(self) -> None:
        """System prompt must document st.tabs() for tabbed interfaces."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "st.tabs()" in layout_section

    def test_contains_container_guidance(self) -> None:
        """System prompt must document st.container() for grouping."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "st.container()" in layout_section

    def test_contains_expander_guidance(self) -> None:
        """System prompt must document st.expander() for collapsible sections."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "st.expander()" in layout_section

    def test_contains_multi_column_example(self) -> None:
        """System prompt must include a multi-column layout example."""
        assert "Multi-Column Layout Example" in SYSTEM_PROMPT

    def test_contains_tabbed_interface_example(self) -> None:
        """System prompt must include a tabbed interface example."""
        assert "Tabbed Interface Example" in SYSTEM_PROMPT

    def test_contains_dashboard_example(self) -> None:
        """System prompt must include a dashboard example."""
        assert "Dashboard Example" in SYSTEM_PROMPT

    def test_contains_expander_example(self) -> None:
        """System prompt must include an expander layout example."""
        assert "Expander Layout Example" in SYSTEM_PROMPT

    def test_layout_examples_use_error_handling(self) -> None:
        """Layout examples must include error handling with specific exceptions."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "except InvalidTickerError" in layout_section
        assert "except RateLimitError" in layout_section
        assert "except MissingApiKeyError" in layout_section
        assert "except ApiError" in layout_section

    def test_layout_examples_use_chart_theme(self) -> None:
        """Layout examples must apply STEGO_LAYOUT for chart theming."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "STEGO_LAYOUT" in layout_section

    def test_layout_examples_use_alpha_vantage(self) -> None:
        """Layout examples must use fetch_daily from alpha_vantage."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "fetch_daily" in layout_section

    def test_contains_layout_checklist(self) -> None:
        """System prompt must include a layout checklist."""
        assert "Layout Checklist" in SYSTEM_PROMPT

    def test_contains_iterative_building_guidance(self) -> None:
        """System prompt must include iterative building guidance."""
        assert "Iterative Building" in SYSTEM_PROMPT

    def test_contains_nesting_rules(self) -> None:
        """System prompt must include nesting rules for layout containers."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "Nesting Rules" in layout_section
        assert "nest" in layout_section.lower()

    def test_contains_modify_remove_layouts(self) -> None:
        """System prompt must include guidance on modifying/removing layouts."""
        assert "Modifying or Removing Layouts" in SYSTEM_PROMPT

    def test_dashboard_example_has_metrics(self) -> None:
        """Dashboard example must include st.metric() for key data points."""
        layout_start = SYSTEM_PROMPT.index("Dashboard Example")
        dashboard_section = SYSTEM_PROMPT[
            layout_start : SYSTEM_PROMPT.index("Expander Layout Example")
        ]
        assert "st.metric" in dashboard_section

    def test_dashboard_example_batches_api_calls(self) -> None:
        """Dashboard example must fetch data up front to minimise API calls."""
        layout_start = SYSTEM_PROMPT.index("Dashboard Example")
        dashboard_section = SYSTEM_PROMPT[
            layout_start : SYSTEM_PROMPT.index("Expander Layout Example")
        ]
        assert "stock_data" in dashboard_section

    def test_layout_examples_use_plotly_chart(self) -> None:
        """Layout examples must use st.plotly_chart with width stretch."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "st.plotly_chart" in layout_section
        assert 'width="stretch"' in layout_section

    def test_tabbed_example_has_multiple_tabs(self) -> None:
        """Tabbed interface example must show multiple tabs."""
        layout_start = SYSTEM_PROMPT.index("Tabbed Interface Example")
        tab_section = SYSTEM_PROMPT[
            layout_start : SYSTEM_PROMPT.index("Dashboard Example")
        ]
        assert "st.tabs(" in tab_section

    def test_iterative_building_mentions_read_tool(self) -> None:
        """Iterative building guidance must mention reading current code."""
        layout_start = SYSTEM_PROMPT.index("Iterative Building")
        iterative_section = SYSTEM_PROMPT[layout_start:]
        assert "Read tool" in iterative_section or "Read" in iterative_section

    def test_layout_checklist_has_nesting_check(self) -> None:
        """Layout checklist must verify proper nesting."""
        layout_start = SYSTEM_PROMPT.index("Layout Checklist")
        checklist_section = SYSTEM_PROMPT[layout_start:]
        assert "nest" in checklist_section.lower()

    def test_performance_guidance_for_dashboards(self) -> None:
        """System prompt must include performance guidance for dashboards."""
        layout_start = SYSTEM_PROMPT.index("Complex Layout Patterns")
        layout_section = SYSTEM_PROMPT[layout_start:]
        assert "rate" in layout_section.lower() or "api call" in layout_section.lower()


# ---------------------------------------------------------------------------
# Options factory tests
# ---------------------------------------------------------------------------


class TestMakeOptions:
    """Verify ClaudeAgentOptions are configured correctly."""

    def test_system_prompt_is_set(self) -> None:
        opts = _make_options()
        assert opts.system_prompt == SYSTEM_PROMPT

    def test_tools_preset(self) -> None:
        opts = _make_options()
        assert opts.tools == {"type": "preset", "preset": "claude_code"}

    def test_permission_mode(self) -> None:
        opts = _make_options()
        assert opts.permission_mode == "bypassPermissions"

    def test_streaming_enabled(self) -> None:
        opts = _make_options()
        assert opts.include_partial_messages is True

    def test_cwd_is_project_root(self) -> None:
        opts = _make_options()
        # cwd should be the parent of agent.py (project root)
        expected = str(Path(__file__).resolve().parent.parent)
        assert opts.cwd == expected

    def test_model_is_set(self) -> None:
        opts = _make_options()
        assert opts.model == "sonnet"


# ---------------------------------------------------------------------------
# Prompt builder tests
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    """Verify conversation history is correctly formatted into a prompt."""

    def test_empty_history(self) -> None:
        prompt = _build_prompt("Hello", [])
        assert prompt == "[User]: Hello"

    def test_single_turn_history(self) -> None:
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        prompt = _build_prompt("How are you?", history)
        assert "[User]: Hi" in prompt
        assert "[Assistant]: Hello!" in prompt
        assert "[User]: How are you?" in prompt

    def test_multi_turn_history(self) -> None:
        history = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Second"},
            {"role": "assistant", "content": "Response 2"},
        ]
        prompt = _build_prompt("Third", history)
        lines = prompt.split("\n\n")
        assert len(lines) == 5  # 4 history + 1 new message

    def test_preserves_order(self) -> None:
        history = [
            {"role": "user", "content": "A"},
            {"role": "assistant", "content": "B"},
        ]
        prompt = _build_prompt("C", history)
        idx_a = prompt.index("[User]: A")
        idx_b = prompt.index("[Assistant]: B")
        idx_c = prompt.index("[User]: C")
        assert idx_a < idx_b < idx_c


# ---------------------------------------------------------------------------
# API key validation tests
# ---------------------------------------------------------------------------


class TestValidateApiKey:
    """Verify API key validation behavior."""

    def test_raises_when_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            # Ensure ANTHROPIC_API_KEY is not present
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(AgentConfigError, match="ANTHROPIC_API_KEY"):
                _validate_api_key()

    def test_raises_when_empty(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with pytest.raises(AgentConfigError, match="ANTHROPIC_API_KEY"):
                _validate_api_key()

    def test_raises_when_whitespace(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "   "}):
            with pytest.raises(AgentConfigError, match="ANTHROPIC_API_KEY"):
                _validate_api_key()

    def test_passes_when_set(self) -> None:
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
            _validate_api_key()  # Should not raise


# ---------------------------------------------------------------------------
# Message extraction tests
# ---------------------------------------------------------------------------


def _make_assistant_message(
    content: list[TextBlock | ToolUseBlock | ToolResultBlock],
) -> AssistantMessage:
    """Helper to create an AssistantMessage with given content blocks."""
    return AssistantMessage(content=content, model="claude-sonnet-4-20250514")


def _make_result_message(
    is_error: bool = False,
    cost: float | None = 0.001,
) -> ResultMessage:
    """Helper to create a ResultMessage."""
    return ResultMessage(
        subtype="result",
        duration_ms=100,
        duration_api_ms=80,
        is_error=is_error,
        num_turns=1,
        session_id="test",
        total_cost_usd=cost,
        usage=None,
        result=None,
        structured_output=None,
    )


class TestExtractAssistantText:
    """Verify text extraction from assistant messages."""

    def test_single_text_block(self) -> None:
        messages = [_make_assistant_message([TextBlock(text="Hello world")])]
        assert extract_assistant_text(messages) == "Hello world"

    def test_multiple_text_blocks(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    TextBlock(text="Hello "),
                    TextBlock(text="world"),
                ]
            )
        ]
        assert extract_assistant_text(messages) == "Hello world"

    def test_ignores_tool_blocks(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    TextBlock(text="Before"),
                    ToolUseBlock(id="t1", name="Read", input={"path": "x.py"}),
                    TextBlock(text="After"),
                ]
            )
        ]
        assert extract_assistant_text(messages) == "BeforeAfter"

    def test_empty_messages(self) -> None:
        assert extract_assistant_text([]) == ""

    def test_ignores_result_messages(self) -> None:
        messages = [_make_result_message()]
        assert extract_assistant_text(messages) == ""

    def test_multiple_assistant_messages(self) -> None:
        messages = [
            _make_assistant_message([TextBlock(text="First ")]),
            _make_assistant_message([TextBlock(text="Second")]),
        ]
        assert extract_assistant_text(messages) == "First Second"


class TestExtractToolCalls:
    """Verify tool call extraction."""

    def test_single_tool_call(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    ToolUseBlock(id="t1", name="Read", input={"path": "app.py"}),
                ]
            )
        ]
        calls = extract_tool_calls(messages)
        assert len(calls) == 1
        assert calls[0]["name"] == "Read"
        assert calls[0]["input"] == {"path": "app.py"}
        assert calls[0]["result"] is None
        assert calls[0]["label"] == "Reading app.py"
        assert calls[0]["icon"] == ":material/description:"

    def test_tool_call_with_result(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    ToolUseBlock(id="t1", name="Edit", input={"file_path": "app.py"}),
                    ToolResultBlock(
                        tool_use_id="t1",
                        content="File edited successfully",
                        is_error=False,
                    ),
                ]
            )
        ]
        calls = extract_tool_calls(messages)
        assert len(calls) == 1
        assert calls[0]["result"] == "File edited successfully"
        assert calls[0]["is_error"] is False
        assert calls[0]["label"] == "Editing app.py"
        assert calls[0]["icon"] == ":material/edit:"

    def test_tool_call_with_error(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    ToolUseBlock(id="t1", name="Bash", input={"command": "bad"}),
                    ToolResultBlock(
                        tool_use_id="t1",
                        content="Command failed",
                        is_error=True,
                    ),
                ]
            )
        ]
        calls = extract_tool_calls(messages)
        assert calls[0]["is_error"] is True
        assert calls[0]["label"] == "Running bad"
        assert calls[0]["icon"] == ":material/terminal:"

    def test_multiple_tool_calls(self) -> None:
        messages = [
            _make_assistant_message(
                [
                    ToolUseBlock(id="t1", name="Read", input={"path": "a.py"}),
                    ToolUseBlock(id="t2", name="Write", input={"path": "b.py"}),
                ]
            )
        ]
        calls = extract_tool_calls(messages)
        assert len(calls) == 2

    def test_empty_messages(self) -> None:
        assert extract_tool_calls([]) == []


# ---------------------------------------------------------------------------
# Format tool label tests
# ---------------------------------------------------------------------------


class TestFormatToolLabel:
    """Verify the format_tool_label helper produces friendly labels and icons."""

    def test_edit_with_path(self) -> None:
        label, icon = format_tool_label("Edit", {"file_path": "/src/app.py"})
        assert label == "Editing app.py"
        assert icon == ":material/edit:"

    def test_write_with_path(self) -> None:
        label, icon = format_tool_label("Write", {"file_path": "output.txt"})
        assert label == "Editing output.txt"
        assert icon == ":material/edit:"

    def test_read_with_path(self) -> None:
        label, icon = format_tool_label("Read", {"path": "config.toml"})
        assert label == "Reading config.toml"
        assert icon == ":material/description:"

    def test_read_with_file_path(self) -> None:
        label, icon = format_tool_label("Read", {"file_path": "/a/b/c.py"})
        assert label == "Reading c.py"
        assert icon == ":material/description:"

    def test_bash_with_command(self) -> None:
        label, icon = format_tool_label("Bash", {"command": "pip install plotly"})
        assert label == "Running pip install plotly"
        assert icon == ":material/terminal:"

    def test_bash_with_long_command(self) -> None:
        long_cmd = "a" * 100
        label, icon = format_tool_label("Bash", {"command": long_cmd})
        assert label.startswith("Running ")
        assert "..." in label
        assert len(label) < 80  # label is reasonably short

    def test_bash_without_command(self) -> None:
        label, icon = format_tool_label("Bash", {})
        assert label == "Running command"
        assert icon == ":material/terminal:"

    def test_web_fetch(self) -> None:
        label, icon = format_tool_label("WebFetch", {"url": "https://example.com"})
        assert label == "Fetching data"
        assert icon == ":material/public:"

    def test_web_search(self) -> None:
        label, icon = format_tool_label("WebSearch", {"query": "test"})
        assert label == "Fetching data"
        assert icon == ":material/public:"

    def test_unknown_tool(self) -> None:
        label, icon = format_tool_label("CustomTool", {"x": 1})
        assert label == "Using CustomTool"
        assert icon == ":material/build:"

    def test_edit_without_path(self) -> None:
        label, icon = format_tool_label("Edit", {})
        assert label == "Editing file"
        assert icon == ":material/edit:"

    def test_read_without_path(self) -> None:
        label, icon = format_tool_label("Read", {})
        assert label == "Reading file"
        assert icon == ":material/description:"

    def test_path_shows_basename_only(self) -> None:
        label, _ = format_tool_label("Read", {"path": "/very/long/path/to/file.py"})
        assert label == "Reading file.py"
        assert "/very/long" not in label


# ---------------------------------------------------------------------------
# Truncate result tests
# ---------------------------------------------------------------------------


class TestTruncateResult:
    """Verify the _truncate_result helper."""

    def test_none_returns_empty(self) -> None:
        assert _truncate_result(None) == ""

    def test_short_string_unchanged(self) -> None:
        assert _truncate_result("hello") == "hello"

    def test_long_string_truncated(self) -> None:
        long_text = "x" * 600
        result = _truncate_result(long_text)
        assert len(result) < 600
        assert "more chars" in result
        assert result.startswith("x" * 500)

    def test_exactly_max_length(self) -> None:
        text = "y" * 500
        result = _truncate_result(text)
        assert result == text  # should not be truncated

    def test_non_string_converted(self) -> None:
        result = _truncate_result(42)
        assert result == "42"

    def test_list_converted(self) -> None:
        result = _truncate_result([1, 2, 3])
        assert result == "[1, 2, 3]"


class TestExtractResult:
    """Verify ResultMessage extraction."""

    def test_returns_result(self) -> None:
        result = _make_result_message()
        messages = [
            _make_assistant_message([TextBlock(text="done")]),
            result,
        ]
        assert extract_result(messages) is result

    def test_returns_none_when_missing(self) -> None:
        messages = [_make_assistant_message([TextBlock(text="hi")])]
        assert extract_result(messages) is None

    def test_empty_messages(self) -> None:
        assert extract_result([]) is None


# ---------------------------------------------------------------------------
# Async query tests (mocked)
# ---------------------------------------------------------------------------


class TestQueryAgent:
    """Verify the async query function behavior with mocked SDK."""

    @pytest.mark.asyncio
    async def test_raises_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(AgentConfigError):
                await query_agent("Hello")

    @pytest.mark.asyncio
    async def test_calls_query_with_correct_args(self) -> None:
        """Verify that the SDK query function is called with proper options."""

        async def mock_query(*, prompt: str, options: object):
            yield _make_assistant_message([TextBlock(text="Hi")])
            yield _make_result_message()

        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("agent.query", side_effect=mock_query),
        ):
            messages = await query_agent("Hello")
            assert len(messages) == 2
            assert isinstance(messages[0], AssistantMessage)
            assert isinstance(messages[1], ResultMessage)

    @pytest.mark.asyncio
    async def test_wraps_sdk_errors(self) -> None:
        """SDK errors should be wrapped in AgentQueryError."""

        async def mock_query(*, prompt: str, options: object):
            raise RuntimeError("SDK failure")
            # Make it an async generator
            yield  # type: ignore[misc]  # pragma: no cover

        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("agent.query", side_effect=mock_query),
        ):
            with pytest.raises(AgentQueryError, match="SDK failure"):
                await query_agent("Hello")

    @pytest.mark.asyncio
    async def test_passes_conversation_history(self) -> None:
        """Conversation history should be included in the prompt."""
        captured_prompt = None

        async def mock_query(*, prompt: str, options: object):
            nonlocal captured_prompt
            captured_prompt = prompt
            yield _make_result_message()

        history = [
            {"role": "user", "content": "prev question"},
            {"role": "assistant", "content": "prev answer"},
        ]
        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("agent.query", side_effect=mock_query),
        ):
            await query_agent("new question", history)
            assert captured_prompt is not None
            assert "prev question" in captured_prompt
            assert "prev answer" in captured_prompt
            assert "new question" in captured_prompt


# ---------------------------------------------------------------------------
# Sync wrapper test
# ---------------------------------------------------------------------------


class TestRunAgentSync:
    """Verify the synchronous wrapper."""

    def test_raises_without_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with pytest.raises(AgentConfigError):
                run_agent_sync("Hello")

    def test_returns_messages(self) -> None:
        """run_agent_sync should return the same messages as query_agent."""

        async def mock_query(*, prompt: str, options: object):
            yield _make_assistant_message([TextBlock(text="sync test")])
            yield _make_result_message()

        with (
            patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}),
            patch("agent.query", side_effect=mock_query),
        ):
            messages = run_agent_sync("Hello")
            assert len(messages) == 2
            text = extract_assistant_text(messages)
            assert text == "sync test"
