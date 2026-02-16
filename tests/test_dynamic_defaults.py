"""Tests for the dynamic_defaults module.

Tests cover the default dynamic section content, the reset function,
and the marker constants used to identify section boundaries.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from dynamic_defaults import (
    DEFAULT_DYNAMIC_SECTION,
    DYNAMIC_END_MARKER,
    DYNAMIC_START_MARKER,
    reset_dynamic_section,
)


# ---------------------------------------------------------------------------
# Marker constants
# ---------------------------------------------------------------------------


class TestMarkerConstants:
    """Verify the marker constants match what is in app.py."""

    def test_start_marker_value(self) -> None:
        assert DYNAMIC_START_MARKER == "# === DYNAMIC START ==="

    def test_end_marker_value(self) -> None:
        assert DYNAMIC_END_MARKER == "# === DYNAMIC END ==="

    def test_markers_present_in_app(self) -> None:
        """app.py must contain both markers."""
        content = Path("app.py").read_text()
        assert DYNAMIC_START_MARKER in content
        assert DYNAMIC_END_MARKER in content


# ---------------------------------------------------------------------------
# Default dynamic section content
# ---------------------------------------------------------------------------


class TestDefaultDynamicSection:
    """Verify the default dynamic section template."""

    def test_is_non_empty_string(self) -> None:
        assert isinstance(DEFAULT_DYNAMIC_SECTION, str)
        assert len(DEFAULT_DYNAMIC_SECTION.strip()) > 0

    def test_contains_example_prompts(self) -> None:
        """Default should define the EXAMPLE_PROMPTS list."""
        assert "EXAMPLE_PROMPTS" in DEFAULT_DYNAMIC_SECTION

    def test_contains_send_callback(self) -> None:
        """Default should define the _send_example_prompt callback."""
        assert "_send_example_prompt" in DEFAULT_DYNAMIC_SECTION

    def test_contains_example_prompt_buttons(self) -> None:
        """Default should render example prompt buttons."""
        assert "example_prompt_0" in DEFAULT_DYNAMIC_SECTION

    def test_contains_empty_state_ui(self) -> None:
        """Default should have the empty state UI with logo and description."""
        assert "logo.jpeg" in DEFAULT_DYNAMIC_SECTION
        assert "Dynamic Data Visualization Agent" in DEFAULT_DYNAMIC_SECTION

    def test_does_not_contain_markers(self) -> None:
        """The default content should NOT include the dynamic markers themselves."""
        assert DYNAMIC_START_MARKER not in DEFAULT_DYNAMIC_SECTION
        assert DYNAMIC_END_MARKER not in DEFAULT_DYNAMIC_SECTION


# ---------------------------------------------------------------------------
# Reset function
# ---------------------------------------------------------------------------


class TestResetDynamicSection:
    """Verify the reset_dynamic_section function."""

    def test_reset_restores_default_content(self, tmp_path: Path) -> None:
        """Reset should replace the dynamic section with defaults."""
        app_file = tmp_path / "app.py"
        app_file.write_text(
            textwrap.dedent("""\
            # Scaffold code
            # === DYNAMIC START ===
            # Some broken code here
            x = 1 / 0
            # === DYNAMIC END ===
        """)
        )

        result = reset_dynamic_section(str(app_file))
        assert result is True

        content = app_file.read_text()
        assert "EXAMPLE_PROMPTS" in content
        assert "_send_example_prompt" in content
        assert "x = 1 / 0" not in content

    def test_reset_preserves_scaffold(self, tmp_path: Path) -> None:
        """Reset should not modify anything outside the dynamic markers."""
        scaffold = "# Scaffold code before\nimport streamlit as st\n"
        after = "\n# Code after dynamic section\n"
        app_file = tmp_path / "app.py"
        app_file.write_text(
            scaffold
            + "# === DYNAMIC START ===\nbroken_code()\n# === DYNAMIC END ==="
            + after
        )

        reset_dynamic_section(str(app_file))

        content = app_file.read_text()
        assert content.startswith(scaffold)
        assert content.endswith(after)

    def test_reset_returns_false_for_missing_file(self, tmp_path: Path) -> None:
        """Should return False if the file does not exist."""
        result = reset_dynamic_section(str(tmp_path / "nonexistent.py"))
        assert result is False

    def test_reset_returns_false_for_missing_markers(self, tmp_path: Path) -> None:
        """Should return False if markers are not found."""
        app_file = tmp_path / "app.py"
        app_file.write_text("# No markers here\n")

        result = reset_dynamic_section(str(app_file))
        assert result is False

    def test_reset_returns_false_for_missing_start_marker(self, tmp_path: Path) -> None:
        """Should return False if only end marker present."""
        app_file = tmp_path / "app.py"
        app_file.write_text("# === DYNAMIC END ===\n")

        result = reset_dynamic_section(str(app_file))
        assert result is False

    def test_reset_returns_false_for_missing_end_marker(self, tmp_path: Path) -> None:
        """Should return False if only start marker present."""
        app_file = tmp_path / "app.py"
        app_file.write_text("# === DYNAMIC START ===\n")

        result = reset_dynamic_section(str(app_file))
        assert result is False

    def test_reset_preserves_marker_lines(self, tmp_path: Path) -> None:
        """After reset, both markers should still be in the file."""
        app_file = tmp_path / "app.py"
        app_file.write_text(
            "# === DYNAMIC START ===\nold_code()\n# === DYNAMIC END ===\n"
        )

        reset_dynamic_section(str(app_file))

        content = app_file.read_text()
        assert DYNAMIC_START_MARKER in content
        assert DYNAMIC_END_MARKER in content

    def test_reset_idempotent(self, tmp_path: Path) -> None:
        """Resetting twice should produce the same result."""
        app_file = tmp_path / "app.py"
        app_file.write_text(
            "# === DYNAMIC START ===\nbroken()\n# === DYNAMIC END ===\n"
        )

        reset_dynamic_section(str(app_file))
        first_content = app_file.read_text()

        reset_dynamic_section(str(app_file))
        second_content = app_file.read_text()

        assert first_content == second_content


# ---------------------------------------------------------------------------
# Integration: verify app.py can be reset
# ---------------------------------------------------------------------------


class TestAppIntegration:
    """Verify that the real app.py can be parsed by the reset function."""

    def test_app_has_both_markers(self) -> None:
        """app.py must contain both dynamic section markers."""
        content = Path("app.py").read_text()
        assert DYNAMIC_START_MARKER in content
        assert DYNAMIC_END_MARKER in content

    def test_start_marker_before_end_marker(self) -> None:
        """DYNAMIC START must appear before DYNAMIC END in app.py."""
        content = Path("app.py").read_text()
        start_idx = content.index(DYNAMIC_START_MARKER)
        end_idx = content.index(DYNAMIC_END_MARKER)
        assert start_idx < end_idx
