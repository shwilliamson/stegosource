# Agent Briefing: design-specs
Generated: 2026-02-16

## Your Task
Add UI/UX specifications to issue #12 (Visual polish and branding with logo).

## Context
- Issue: #12 - Visual polish and branding with logo
- This issue involves UI work and needs design specifications before implementation
- The app is a Streamlit-based data visualization agent called "Stegosource"
- The app uses a dark theme (see `.streamlit/config.toml`)
- The logo is at `logo.jpeg` in the repo root

## Current State
The app already has:
- A sidebar with `st.image("logo.jpeg", width=200)` and chat interface below it
- A main content area with a centered logo (width=280), caption, description, and example prompt buttons
- Page config: `st.set_page_config(page_title="Stegosource", page_icon="🦕", layout="wide")`
- Dark theme configured in `.streamlit/config.toml`:
  - primaryColor: #00D4FF (cyan)
  - backgroundColor: #0E1117 (dark)
  - secondaryBackgroundColor: #1A1D26 (slightly lighter dark)
  - textColor: #FAFAFA (near-white)

## Acceptance Criteria from Issue
- [ ] `logo.jpeg` displayed in the app (sidebar header or main area header) at its original aspect ratio
- [ ] Consistent visual hierarchy: clear typography scale for headings, subheadings, and body text
- [ ] Clean spacing between sections (chat area, dynamic content area, charts)
- [ ] Streamlit page config uses the app name and a relevant icon
- [ ] Sidebar has a branded header (logo + app name) above the chat interface
- [ ] Visual distinction between the chat area and the dynamic content area
- [ ] Use `st.divider()` or spacing to separate content groups in the main area
- [ ] Overall look feels cohesive -- not default Streamlit gray-on-gray

## Technical Notes from Issue
- Use `st.image("logo.jpeg", use_container_width=False)` to preserve the original aspect ratio
- Streamlit supports custom CSS via `st.markdown()` with `unsafe_allow_html=True` for minor styling tweaks
- Keep customizations minimal -- lean on Streamlit's built-in components and theming where possible
- Consider Streamlit's built-in theme configuration (`.streamlit/config.toml`) for primary colors

## Resources (Read as Needed)
- Issue details: `gh issue view 12`
- Current app code: `app.py`
- Theme config: `.streamlit/config.toml`
- Logo: `logo.jpeg`

## Expected Output
Post design specifications as an issue comment following your AGENT.md template, including:
- Design intent
- User flow
- Visual design with token references
- Component states
- Accessibility requirements
- Responsive behavior
