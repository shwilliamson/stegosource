"""Default dynamic section content for workspace reset.

This module stores the original content of app.py's dynamic section
(between ``# === DYNAMIC START ===`` and ``# === DYNAMIC END ===``).
The reset mechanism uses this to restore the workspace to its initial state.
"""

from __future__ import annotations

DEFAULT_DYNAMIC_SECTION: str = '''\
try:
    # Agent-generated UI goes here. The agent may freely add, modify, or remove
    # any Streamlit or Plotly code in this section.

    # ---------------------------------------------------------------------------
    # Default empty state \u2014 shown until the agent modifies this section
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
        st.image("logo.jpeg", width="content")
        st.caption("Dynamic Data Visualization Agent")
        st.write(
            "Ask Stegosource to fetch financial data, build interactive charts, "
            "and create dashboards \\u2014 all through natural conversation."
        )

        st.divider()

        # 2x2 grid of example prompt cards
        _row1_left, _row1_right = st.columns(2)
        _row2_left, _row2_right = st.columns(2)

        with _row1_left:
            st.button(
                EXAMPLE_PROMPTS[0],
                key="example_prompt_0",
                width="stretch",
                on_click=_send_example_prompt,
                args=(EXAMPLE_PROMPTS[0],),
            )
        with _row1_right:
            st.button(
                EXAMPLE_PROMPTS[1],
                key="example_prompt_1",
                width="stretch",
                on_click=_send_example_prompt,
                args=(EXAMPLE_PROMPTS[1],),
            )
        with _row2_left:
            st.button(
                EXAMPLE_PROMPTS[2],
                key="example_prompt_2",
                width="stretch",
                on_click=_send_example_prompt,
                args=(EXAMPLE_PROMPTS[2],),
            )
        with _row2_right:
            st.button(
                EXAMPLE_PROMPTS[3],
                key="example_prompt_3",
                width="stretch",
                on_click=_send_example_prompt,
                args=(EXAMPLE_PROMPTS[3],),
            )

except Exception:  # noqa: BLE001
    # ---------------------------------------------------------------------------
    # Dynamic section error recovery \u2014 display the traceback so the user (and
    # the agent) can see what went wrong, while keeping the scaffold functional.
    # ---------------------------------------------------------------------------
    st.error(
        "**The dynamic section encountered an error.** "
        "The chat interface is still available in the sidebar \\u2014 "
        "ask the agent to fix the issue, or use the **Reset Workspace** button."
    )
    st.exception(Exception(traceback.format_exc()))
'''

# Markers used to identify the dynamic section boundaries in app.py
DYNAMIC_START_MARKER: str = "# === DYNAMIC START ==="
DYNAMIC_END_MARKER: str = "# === DYNAMIC END ==="


def reset_dynamic_section(app_path: str = "app.py") -> bool:
    """Reset the dynamic section of app.py to its default content.

    Reads the current ``app.py``, replaces everything between the dynamic
    markers with :data:`DEFAULT_DYNAMIC_SECTION`, and writes the file back.

    Parameters
    ----------
    app_path:
        Path to the app file to reset.  Defaults to ``"app.py"``.

    Returns
    -------
    bool
        ``True`` if the reset succeeded, ``False`` if the markers could not
        be found or the write failed.
    """
    from pathlib import Path

    path = Path(app_path)
    if not path.exists():
        return False

    content = path.read_text()

    start_idx = content.find(DYNAMIC_START_MARKER)
    end_idx = content.find(DYNAMIC_END_MARKER)

    if start_idx == -1 or end_idx == -1:
        return False

    # Reconstruct the file: everything before DYNAMIC START marker,
    # the marker line, the default content, and everything from DYNAMIC END onward
    before = content[: start_idx + len(DYNAMIC_START_MARKER)]
    after = content[end_idx:]

    new_content = before + "\n" + DEFAULT_DYNAMIC_SECTION + "\n" + after
    path.write_text(new_content)
    return True
