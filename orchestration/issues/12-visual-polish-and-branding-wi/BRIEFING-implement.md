# Agent Briefing: implement
Generated: 2026-02-16

## Your Task
Implement issue #12: Visual polish and branding with logo

## Context
- Mode: all-issues (auto-merge handled by orchestrator)
- This is a UI polish task for a Streamlit app called "Stegosource"
- The app uses a dark theme configured in `.streamlit/config.toml`
- The main app file is `app.py`

## IMPORTANT: Scaffold Rules
The file `app.py` has clearly marked sections:
- **SCAFFOLD section** (between `=== SCAFFOLD START ===` and `=== SCAFFOLD END ===`): You MUST modify this section for sidebar branding changes — the sidebar code is here
- **DYNAMIC section** (between `=== DYNAMIC START ===` and `=== DYNAMIC END ===`): You may modify this section for main content area changes

Note: Despite the scaffold warning "Do NOT edit between scaffold markers", you MUST edit within the scaffold section for this issue because the sidebar branding code lives there. The acceptance criteria explicitly require changes to the sidebar header.

## Acceptance Criteria
- [ ] `logo.jpeg` displayed in the app (sidebar header or main area header) at its original aspect ratio
- [ ] Consistent visual hierarchy: clear typography scale for headings, subheadings, and body text
- [ ] Clean spacing between sections (chat area, dynamic content area, charts)
- [ ] Streamlit page config uses the app name and a relevant icon
- [ ] Sidebar has a branded header (logo + app name) above the chat interface
- [ ] Visual distinction between the chat area and the dynamic content area
- [ ] Use `st.divider()` or spacing to separate content groups in the main area
- [ ] Overall look feels cohesive -- not default Streamlit gray-on-gray

## Prior Agent Activity
- **Designer**: Created UI specifications (posted as issue #12 comment). Key design decisions:
  - Sidebar: branded header with logo (use_container_width=False, ~60-80px width area) + "Stegosource" heading + tagline caption, then `st.divider()`, then chat
  - Main area empty state: centered logo, tagline caption, description, `st.divider()`, then example prompt grid
  - Use Streamlit native components over custom CSS
  - Keep existing dark theme from config.toml
  - Minimal custom CSS only if needed for layout fine-tuning

## Implementation Guidance

### Sidebar Changes (in SCAFFOLD section)
Currently the sidebar has:
```python
with st.sidebar:
    st.image("logo.jpeg", width=200)
    # ... chat messages and input
```

Change to:
```python
with st.sidebar:
    st.image("logo.jpeg", use_container_width=False)
    st.markdown("### Stegosource")
    st.caption("Dynamic Data Visualization Agent")
    st.divider()
    # ... rest of chat messages and input
```

### Main Content Area (in DYNAMIC section)
Currently has centered logo, caption, description, and buttons. Add:
- A `st.divider()` between the description and the example prompt buttons
- Ensure the main area description text is clear and well-spaced

### Page Config
Already set correctly:
```python
st.set_page_config(page_title="Stegosource", page_icon="🦕", layout="wide")
```
No changes needed.

### Tests
- Run `ruff check .` and `ruff format .` to ensure code quality
- Run `pytest` to ensure no regressions

## Resources (Read as Needed)
- Issue details: `gh issue view 12`
- Design specs: Check issue #12 comments for "[Designer] Design Specifications"
- Current app code: `app.py`
- Theme config: `.streamlit/config.toml`

## Expected Output
- Working implementation matching acceptance criteria
- All tests and linting passing
- PR created with "Closes #12" in body
- Branch name: `12-visual-polish-and-branding`
