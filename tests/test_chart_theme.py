"""Tests for the chart_theme module.

Verifies that the Plotly theming constants are correct and produce valid
Plotly layout configurations.
"""

from __future__ import annotations

from typing import Any

import plotly.express as px
import plotly.graph_objects as go

from chart_theme import (
    CANDLESTICK_DOWN,
    CANDLESTICK_UP,
    CHART_COLORS,
    STEGO_LAYOUT,
)


# ---------------------------------------------------------------------------
# Constant value tests
# ---------------------------------------------------------------------------


class TestChartColors:
    """Verify the chart color palette."""

    def test_has_at_least_eight_colors(self) -> None:
        assert len(CHART_COLORS) >= 8

    def test_all_hex_format(self) -> None:
        """Each color should be a valid hex color string."""
        for color in CHART_COLORS:
            assert color.startswith("#"), f"Color {color} is not hex"
            assert len(color) == 7, f"Color {color} is not 7-char hex"

    def test_primary_color_is_brand_cyan(self) -> None:
        """First color should be brand cyan."""
        assert CHART_COLORS[0] == "#00D4FF"

    def test_no_duplicate_colors(self) -> None:
        """All colors should be unique."""
        assert len(set(CHART_COLORS)) == len(CHART_COLORS)


class TestCandlestickColors:
    """Verify candlestick direction colors match design system."""

    def test_up_color_is_brand_green(self) -> None:
        assert CANDLESTICK_UP == "#00E676"

    def test_down_color_is_brand_magenta(self) -> None:
        assert CANDLESTICK_DOWN == "#E040A0"

    def test_up_and_down_are_different(self) -> None:
        assert CANDLESTICK_UP != CANDLESTICK_DOWN


# ---------------------------------------------------------------------------
# Layout template tests
# ---------------------------------------------------------------------------


class TestStegoLayout:
    """Verify the STEGO_LAYOUT template structure and values."""

    def test_is_dict(self) -> None:
        assert isinstance(STEGO_LAYOUT, dict)

    def test_transparent_backgrounds(self) -> None:
        """Chart backgrounds should be transparent."""
        assert STEGO_LAYOUT["paper_bgcolor"] == "rgba(0,0,0,0)"
        assert STEGO_LAYOUT["plot_bgcolor"] == "rgba(0,0,0,0)"

    def test_font_configuration(self) -> None:
        """Font should use Source Sans Pro and be light-colored."""
        font = STEGO_LAYOUT["font"]
        assert "Source Sans Pro" in font["family"]
        assert font["color"] == "#FAFAFA"
        assert font["size"] > 0

    def test_title_configuration(self) -> None:
        """Title should be left-aligned with proper sizing."""
        title = STEGO_LAYOUT["title"]
        assert title["x"] == 0
        assert title["xanchor"] == "left"
        assert title["font"]["size"] == 20

    def test_axis_grid_colors(self) -> None:
        """Axis grid colors should match border-default from design system."""
        for axis in ("xaxis", "yaxis"):
            assert STEGO_LAYOUT[axis]["gridcolor"] == "#333844"
            assert STEGO_LAYOUT[axis]["zerolinecolor"] == "#333844"

    def test_axis_tick_font(self) -> None:
        """Axis ticks should use text-secondary color."""
        for axis in ("xaxis", "yaxis"):
            assert STEGO_LAYOUT[axis]["tickfont"]["color"] == "#A0A8B8"

    def test_legend_transparent_background(self) -> None:
        """Legend background should be transparent."""
        assert STEGO_LAYOUT["legend"]["bgcolor"] == "rgba(0,0,0,0)"

    def test_hoverlabel_styling(self) -> None:
        """Hover labels should use bg-elevated from design system."""
        hover = STEGO_LAYOUT["hoverlabel"]
        assert hover["bgcolor"] == "#262A36"
        assert hover["font_color"] == "#FAFAFA"
        assert hover["bordercolor"] == "#333844"

    def test_colorway_matches_chart_colors(self) -> None:
        """Layout colorway should use the CHART_COLORS palette."""
        assert STEGO_LAYOUT["colorway"] == CHART_COLORS

    def test_margins_defined(self) -> None:
        """Layout should have explicit margins."""
        margin = STEGO_LAYOUT["margin"]
        assert all(k in margin for k in ("l", "r", "t", "b"))
        assert all(v > 0 for v in margin.values())


# ---------------------------------------------------------------------------
# Integration tests — verify the layout produces valid Plotly figures
# ---------------------------------------------------------------------------


class TestStegoLayoutIntegration:
    """Verify that STEGO_LAYOUT can be applied to actual Plotly figures."""

    _sample_data: list[dict[str, Any]] = [
        {
            "date": "2025-01-13",
            "open": 150.0,
            "high": 155.0,
            "low": 148.0,
            "close": 152.0,
            "volume": 1000000,
        },
        {
            "date": "2025-01-14",
            "open": 152.0,
            "high": 157.0,
            "low": 150.0,
            "close": 154.0,
            "volume": 1100000,
        },
        {
            "date": "2025-01-15",
            "open": 154.0,
            "high": 158.0,
            "low": 151.0,
            "close": 156.0,
            "volume": 1200000,
        },
    ]

    def test_apply_to_line_chart(self) -> None:
        """STEGO_LAYOUT should apply cleanly to a Plotly Express line chart."""
        fig = px.line(
            self._sample_data,
            x="date",
            y="close",
            title="Test line chart",
            labels={"date": "Date", "close": "Price (USD)"},
        )
        fig.update_layout(**STEGO_LAYOUT)
        layout = fig.to_dict()["layout"]
        assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"
        assert layout["plot_bgcolor"] == "rgba(0,0,0,0)"
        assert layout["title"]["text"] == "Test line chart"

    def test_apply_to_candlestick_chart(self) -> None:
        """STEGO_LAYOUT should apply cleanly to a candlestick chart."""
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=[r["date"] for r in self._sample_data],
                    open=[r["open"] for r in self._sample_data],
                    high=[r["high"] for r in self._sample_data],
                    low=[r["low"] for r in self._sample_data],
                    close=[r["close"] for r in self._sample_data],
                    increasing=dict(
                        line=dict(color=CANDLESTICK_UP), fillcolor=CANDLESTICK_UP
                    ),
                    decreasing=dict(
                        line=dict(color=CANDLESTICK_DOWN), fillcolor=CANDLESTICK_DOWN
                    ),
                    name="TEST",
                )
            ]
        )
        # Apply theme first, then chart-specific properties
        fig.update_layout(**STEGO_LAYOUT)
        fig.update_layout(
            title_text="Test candlestick chart",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
        )
        layout = fig.to_dict()["layout"]
        assert layout["paper_bgcolor"] == "rgba(0,0,0,0)"
        assert layout["xaxis"]["rangeslider"]["visible"] is False
        assert layout["title"]["text"] == "Test candlestick chart"

        # Verify candlestick colors
        candle_data = fig.to_dict()["data"][0]
        assert candle_data["increasing"]["line"]["color"] == CANDLESTICK_UP
        assert candle_data["decreasing"]["line"]["color"] == CANDLESTICK_DOWN

    def test_apply_to_multi_trace_chart(self) -> None:
        """STEGO_LAYOUT should work with multiple traces using add_trace."""
        fig = go.Figure()
        for name, offset in [("AAPL", 0), ("GOOGL", 10)]:
            fig.add_trace(
                go.Scatter(
                    x=[r["date"] for r in self._sample_data],
                    y=[r["close"] + offset for r in self._sample_data],
                    mode="lines",
                    name=name,
                )
            )
        # Apply theme first, then chart-specific properties
        fig.update_layout(**STEGO_LAYOUT)
        fig.update_layout(
            title_text="Multi-symbol comparison",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
        )
        chart_dict = fig.to_dict()
        assert len(chart_dict["data"]) == 2
        assert chart_dict["data"][0]["name"] == "AAPL"
        assert chart_dict["data"][1]["name"] == "GOOGL"

    def test_figure_serializable(self) -> None:
        """A themed figure should be JSON-serializable (Plotly requirement)."""
        fig = px.line(
            self._sample_data,
            x="date",
            y="close",
            title="Serialization test",
        )
        fig.update_layout(**STEGO_LAYOUT)
        # to_json() would throw if not serializable
        json_str = fig.to_json()
        assert len(json_str) > 0
