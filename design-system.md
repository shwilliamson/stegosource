# Stegosource Design System

A comprehensive design language for Stegosource — a dynamic data visualization agent powered by the Anthropic Agent SDK and Streamlit.

---

## Design Philosophy

Stegosource is a technical capability demo. The design should communicate **competence and clarity** — it is a tool that does impressive things, and the UI should stay out of the way while making those things visible. The brand identity is rooted in the logo: a circuit-board stegosaurus with data visualization plates, rendered in neon cyan against a dark background.

**Guiding principles:**

1. **Dark-first, data-forward.** Dark backgrounds make charts pop and signal a technical/data tool.
2. **Restrained color.** Mostly neutral darks and grays. Color is reserved for brand accents, data, and semantic states.
3. **Visible intelligence.** Tool calls, streaming text, and state changes should feel transparent — the user sees the agent working.
4. **Streamlit-native.** Work with the framework, not against it. Use `config.toml` theming as the primary styling mechanism. Use `st.markdown` CSS injection sparingly and only for polish that the theme system cannot achieve.

---

## Color Palette

### Brand Colors

Derived from the logo's neon aesthetic, but toned down for UI use.

| Token | Hex | Usage |
|-------|-----|-------|
| `brand-cyan` | `#00D4FF` | Primary accent. Interactive elements, links, active states. |
| `brand-cyan-muted` | `#0099CC` | Hover states, secondary emphasis. |
| `brand-cyan-subtle` | `#003D4D` | Backgrounds for highlighted regions, selected items. |
| `brand-magenta` | `#E040A0` | Secondary accent. Candlestick down, chart highlights, badges. |
| `brand-magenta-muted` | `#A62D72` | Hover variant for magenta elements. |
| `brand-green` | `#00E676` | Candlestick up, positive values, success confirmation. |
| `brand-green-muted` | `#00B85C` | Hover variant for green elements. |

### Neutral Colors (Dark Theme)

| Token | Hex | Usage |
|-------|-----|-------|
| `bg-primary` | `#0E1117` | App background (Streamlit dark default). |
| `bg-secondary` | `#1A1D26` | Sidebar background, card surfaces, grouped sections. |
| `bg-elevated` | `#262A36` | Elevated surfaces: tooltips, dropdowns, expandable sections. |
| `bg-hover` | `#2E3344` | Hover state backgrounds. |
| `border-default` | `#333844` | Default borders, dividers, separators. |
| `border-subtle` | `#262A36` | Subtle separation (e.g., between chat messages). |
| `border-emphasis` | `#4A5068` | Emphasized borders (focused inputs, active cards). |

### Text Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#FAFAFA` | Primary text (headings, body). |
| `text-secondary` | `#A0A8B8` | Secondary text (labels, captions, timestamps). |
| `text-tertiary` | `#787E8C` | Tertiary text (placeholders, disabled text). |
| `text-on-accent` | `#0E1117` | Text on bright accent backgrounds. |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `success` | `#00E676` | Success states, positive data, confirmations. |
| `success-bg` | `#00E6761A` | Success background (10% opacity). |
| `warning` | `#FFB020` | Warnings, rate limit notices. |
| `warning-bg` | `#FFB0201A` | Warning background. |
| `error` | `#F04848` | Errors, failures, destructive actions. |
| `error-bg` | `#F048481A` | Error background. |
| `info` | `#00D4FF` | Informational messages (maps to brand-cyan). |
| `info-bg` | `#00D4FF1A` | Info background. |

### Chart Data Colors

A sequential palette for multi-series charts. Ordered for visual distinction.

| Index | Hex | Name |
|-------|-----|------|
| 1 | `#00D4FF` | Cyan (primary series) |
| 2 | `#E040A0` | Magenta |
| 3 | `#00E676` | Green |
| 4 | `#FFB020` | Amber |
| 5 | `#8B5CF6` | Violet |
| 6 | `#F04848` | Red |
| 7 | `#06B6D4` | Teal |
| 8 | `#F59E0B` | Orange |

---

## Streamlit Theme Configuration

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#00D4FF"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1A1D26"
textColor = "#FAFAFA"
font = "sans serif"
headingFont = "sans serif"
codeFont = "monospace"

# Borders and radii
borderColor = "#333844"
baseRadius = "small"
buttonRadius = "small"

[theme.sidebar]
backgroundColor = "#1A1D26"
textColor = "#FAFAFA"
```

### CSS Custom Properties (Injected via `st.markdown`)

Use these for any custom-styled elements. Inject once at app startup in the scaffold section.

```python
CUSTOM_CSS = """
<style>
:root {
    /* Brand */
    --stego-cyan: #00D4FF;
    --stego-cyan-muted: #0099CC;
    --stego-cyan-subtle: #003D4D;
    --stego-magenta: #E040A0;
    --stego-green: #00E676;

    /* Surfaces */
    --stego-bg-primary: #0E1117;
    --stego-bg-secondary: #1A1D26;
    --stego-bg-elevated: #262A36;
    --stego-bg-hover: #2E3344;

    /* Borders */
    --stego-border: #333844;
    --stego-border-subtle: #262A36;
    --stego-border-emphasis: #4A5068;

    /* Text */
    --stego-text-primary: #FAFAFA;
    --stego-text-secondary: #A0A8B8;
    --stego-text-tertiary: #787E8C;

    /* Semantic */
    --stego-success: #00E676;
    --stego-warning: #FFB020;
    --stego-error: #F04848;
    --stego-info: #00D4FF;

    /* Spacing */
    --stego-space-xs: 4px;
    --stego-space-sm: 8px;
    --stego-space-md: 16px;
    --stego-space-lg: 24px;
    --stego-space-xl: 32px;
    --stego-space-2xl: 48px;

    /* Radii */
    --stego-radius-sm: 4px;
    --stego-radius-md: 8px;
    --stego-radius-lg: 12px;
    --stego-radius-full: 9999px;

    /* Transitions */
    --stego-transition-fast: 150ms ease;
    --stego-transition-normal: 250ms ease;
}
</style>
"""
```

---

## Typography

Stegosource uses Streamlit's built-in font stack. No custom fonts are loaded — this avoids flash-of-unstyled-text and keeps the app fast.

### Font Stack

| Context | Config Value | Rendered As |
|---------|-------------|-------------|
| Headings | `sans serif` | Source Sans Pro (Streamlit default) |
| Body text | `sans serif` | Source Sans Pro |
| Code / tool output | `monospace` | Source Code Pro |

### Type Scale

Use Streamlit's built-in heading hierarchy. For custom-styled text, follow this scale:

| Level | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| Display | 28px / 1.75rem | 700 | 1.2 | App title only |
| H1 | 24px / 1.5rem | 700 | 1.3 | Section headers (chart titles) |
| H2 | 20px / 1.25rem | 600 | 1.35 | Subsection headers |
| H3 | 16px / 1rem | 600 | 1.4 | Card headers, group labels |
| Body | 14px / 0.875rem | 400 | 1.5 | Default body text, chat messages |
| Caption | 12px / 0.75rem | 400 | 1.4 | Timestamps, labels, secondary info |
| Code | 13px / 0.8125rem | 400 | 1.5 | Tool call output, code blocks |

### Text Style Guidelines

- **Headings**: Sentence case ("Stock price comparison"), not title case.
- **Labels**: Short, direct. "Date range" not "Please select a date range."
- **Agent messages**: Natural language, no excessive punctuation or emoji.
- **Tool call labels**: Verb-first, concise. "Editing app.py", "Fetching AAPL data."
- **Error messages**: State the problem, then the remedy. "Rate limit reached. Try again in 60 seconds."

---

## Spacing & Layout

### Spacing Scale

Based on a 4px base unit. Use consistently for padding, margins, and gaps.

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Inline spacing, icon gaps |
| `sm` | 8px | Tight grouping, between related elements |
| `md` | 16px | Standard spacing, padding inside cards |
| `lg` | 24px | Between sections, card margins |
| `xl` | 32px | Major section separation |
| `2xl` | 48px | Page-level vertical rhythm |

### Layout Structure

```
+--------------------------------------------+
|  SIDEBAR (chat)  |    MAIN AREA (content)  |
|  ~350px fixed    |    Fluid, fills rest     |
|                  |                          |
|  [Logo]          |  [Agent-generated UI]    |
|  [Chat history]  |  - Charts               |
|  [Tool calls]    |  - Forms                 |
|  [Chat input]    |  - Dashboards            |
|                  |  - Empty state           |
+--------------------------------------------+
```

- **Page layout**: `st.set_page_config(layout="wide")` — always.
- **Sidebar width**: Streamlit default (~350px). Do not fight this.
- **Main area padding**: Streamlit's default padding is sufficient. Do not add extra wrappers.
- **Columns**: Use `st.columns()` with intentional ratios. Common patterns:
  - Single chart: full width, no columns.
  - Chart + controls: `[3, 1]` ratio (chart gets 75%).
  - Dashboard: `[1, 1]` for two equal panels, `[1, 1, 1]` for three.
  - Form inputs: `[1, 1]` for side-by-side fields, single column for stacked forms.

### Container Patterns

- **Chart containers**: Use `st.container()` with optional `border=True` for grouped sections.
- **Tabs**: `st.tabs()` for switching between views in dashboards.
- **Expanders**: `st.expander()` for optional detail (tool calls, advanced settings).

---

## Components

### Chat Messages

Chat lives in the sidebar using `st.chat_message()` and `st.chat_input()`.

#### User Message
- **Avatar**: Streamlit default user icon.
- **Background**: `bg-secondary` (inherited from sidebar).
- **Text**: `text-primary`, Body size (14px).
- **Alignment**: Left-aligned (Streamlit default).

#### Assistant Message
- **Avatar**: Stegosaurus emoji or custom icon.
- **Background**: `bg-secondary` (inherited from sidebar).
- **Text**: `text-primary`, Body size (14px).
- **Streaming indicator**: Blinking cursor or Streamlit's built-in streaming animation.

#### Message Guidelines
- Keep the chat area uncluttered. Messages should be concise.
- Long agent responses should use expandable sections for detail.
- No custom bubble styling — use Streamlit's native `st.chat_message` appearance.

### Tool Call Display

Tool calls are shown inline within assistant messages using `st.expander()`.

| Element | Style |
|---------|-------|
| Container | `st.expander()` inside `st.chat_message("assistant")` |
| Label format | Icon + verb phrase: "Editing app.py", "Fetching AAPL data" |
| Label color | `text-secondary` (#A0A8B8) |
| Expanded content | Monospace code block showing tool input/output |
| Icon by tool type | Write/Edit: pencil, Bash: terminal, API: globe, Read: document |

**Tool type icons (Unicode):**

| Tool | Icon | Label Example |
|------|------|---------------|
| Write/Edit file | pencil | "Editing app.py" |
| Read file | document | "Reading app.py" |
| Bash command | terminal | "Running pip install plotly" |
| Alpha Vantage | chart | "Fetching AAPL daily data" |
| Code execution | gear | "Generating chart code" |

**Implementation pattern:**
```python
with st.chat_message("assistant"):
    st.write("Let me create that chart for you.")
    with st.expander("Fetching AAPL data", icon=":material/public:"):
        st.code(tool_output, language="json")
    with st.expander("Editing app.py", icon=":material/edit:"):
        st.code(file_diff, language="python")
```

### Empty State

Displayed in the main area before the agent has generated any content.

| Element | Style |
|---------|-------|
| Container | Centered in main area, `max-width: 640px` (use `st.columns([1,2,1])` centering) |
| Logo | `logo.jpeg` displayed via `st.image()`, max-width 280px, centered |
| Tagline | "Dynamic Data Visualization Agent" — `text-secondary`, Caption size |
| Description | 1-2 sentences about what the app does — `text-secondary`, Body size |
| Prompt cards | 3-4 clickable example prompts |

#### Example Prompt Cards

Each card is a `st.button()` with `use_container_width=True` inside a column layout.

| Element | Style |
|---------|-------|
| Layout | 2x2 grid using `st.columns([1, 1])` |
| Button style | Full-width, secondary style (Streamlit default) |
| Text | Short prompt, left-aligned. e.g., "Show me AAPL stock for the last 3 months" |
| Hover | Streamlit default button hover (slight highlight) |
| Behavior | On click, populate chat input and send message |

**Example prompts:**
1. "Show me AAPL stock for the last 3 months"
2. "Compare TSLA and MSFT performance"
3. "Add a date range picker for the chart"
4. "Create a candlestick chart for GOOGL"

### Chart Containers

Charts are rendered in the main area via `st.plotly_chart()`.

| Element | Style |
|---------|-------|
| Render call | `st.plotly_chart(fig, use_container_width=True)` |
| Background | Transparent (inherits app background) |
| Title | Set via Plotly `fig.update_layout(title=...)`, H2 size equivalent |
| Grid lines | `#333844` (matches `border-default`) |
| Axis text | `text-secondary` (#A0A8B8) |
| Data colors | Use the chart data palette defined above |
| Hover labels | `bg-elevated` background, `text-primary` text |

#### Plotly Theme Template

The agent should use this Plotly layout template when generating charts:

```python
PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans Pro, sans-serif", color="#FAFAFA", size=13),
        title=dict(font=dict(size=20, color="#FAFAFA"), x=0, xanchor="left"),
        xaxis=dict(
            gridcolor="#333844",
            zerolinecolor="#333844",
            tickfont=dict(color="#A0A8B8", size=12),
            title=dict(font=dict(color="#A0A8B8", size=13)),
        ),
        yaxis=dict(
            gridcolor="#333844",
            zerolinecolor="#333844",
            tickfont=dict(color="#A0A8B8", size=12),
            title=dict(font=dict(color="#A0A8B8", size=13)),
        ),
        legend=dict(
            font=dict(color="#A0A8B8", size=12),
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor="#262A36",
            font_size=13,
            font_color="#FAFAFA",
            bordercolor="#333844",
        ),
        colorway=[
            "#00D4FF", "#E040A0", "#00E676", "#FFB020",
            "#8B5CF6", "#F04848", "#06B6D4", "#F59E0B",
        ],
        margin=dict(l=48, r=24, t=56, b=48),
    )
)
```

#### Candlestick Chart Colors

| Direction | Color |
|-----------|-------|
| Up (close > open) | `brand-green` (#00E676) |
| Down (close < open) | `brand-magenta` (#E040A0) |

### Form Inputs & Controls

Agent-generated forms use standard Streamlit widgets. Styling comes from the theme.

| Widget | Notes |
|--------|-------|
| `st.text_input()` | Use concise labels. Placeholder text for examples. |
| `st.selectbox()` | Use for lists under 10 items. |
| `st.multiselect()` | Use for multi-symbol selection. |
| `st.date_input()` | Use for date ranges. Pair two for start/end. |
| `st.slider()` | Use for numeric ranges (e.g., moving average window). |
| `st.number_input()` | Use for precise numeric entry (e.g., price alerts). |
| `st.form()` + `st.form_submit_button()` | Wrap related inputs to batch submissions. |

**Form layout guidelines:**
- Group related inputs with `st.columns()`.
- Submit buttons should use `type="primary"` to pick up the `brand-cyan` accent.
- Place forms above the chart they control, or in a sidebar section.
- Label every input. Never rely on placeholder text alone.

### Buttons

| Variant | Streamlit API | Visual |
|---------|--------------|--------|
| Primary | `st.button("Label", type="primary")` | `brand-cyan` background, `text-on-accent` text |
| Secondary | `st.button("Label")` | Transparent background, `brand-cyan` border and text |
| Danger | Custom CSS class (rare) | `error` background, white text |

### Status Indicators

| State | Implementation | Visual |
|-------|---------------|--------|
| Loading / thinking | `st.spinner("Thinking...")` | Streamlit's default spinner with custom text |
| Streaming text | `st.write_stream()` or manual token append | Text appears progressively, no special styling |
| Success | `st.success("Chart updated")` | Green left border, `success-bg` background |
| Warning | `st.warning("Rate limit: 25/day")` | Amber left border, `warning-bg` background |
| Error | `st.error("Failed to fetch data")` | Red left border, `error-bg` background |
| Info | `st.info("Tip: Try asking...")` | Cyan left border, `info-bg` background |
| Toast | `st.toast("Saved!")` | Appears bottom-right, auto-dismisses |

---

## Interaction Patterns

### Streaming Text

- Use Streamlit's `st.write_stream()` for agent responses when available.
- Text should appear progressively, word by word or chunk by chunk.
- No artificial delays. Display tokens as fast as they arrive.
- The chat input should be disabled or show a spinner while streaming.

### Hot-Reload Transitions

- When the agent edits `app.py`, Streamlit reruns the script automatically.
- Session state (chat history) persists across reruns by design.
- The main area content will re-render. This is expected and acceptable.
- No custom transition animations needed. Streamlit handles the rerun cleanly.
- If the agent adds a new chart, it simply appears on the next rerun.

### Loading States

1. **Agent thinking**: `st.spinner("Thinking...")` in the sidebar while the agent processes.
2. **Tool execution**: Tool call expander appears immediately with label, content fills in when complete.
3. **Data fetching**: Spinner or status message: "Fetching AAPL daily data..."
4. **File editing**: Tool call expander shows "Editing app.py" — the hot-reload handles the visual update.

### Hover & Focus

- **Buttons**: Streamlit default hover (slight background change). No custom hover needed.
- **Expanders**: Streamlit default hover on the expander header.
- **Chat input**: Streamlit default focus ring (uses `primaryColor`).
- **Links**: `brand-cyan`, underline on hover.

### Error Recovery

- If the agent breaks `app.py`, the Streamlit error page will appear.
- A "Reset workspace" mechanism (issue #11) restores `app.py` to the default scaffold.
- Error messages in chat should be actionable: tell the user what went wrong and what to try.

---

## Accessibility Standards

### Color Contrast (WCAG 2.1 AA)

All text meets minimum contrast ratios against their intended background:

| Combination | Ratio | Status |
|-------------|-------|--------|
| `text-primary` (#FAFAFA) on `bg-primary` (#0E1117) | 18.1:1 | Pass (AAA) |
| `text-primary` (#FAFAFA) on `bg-secondary` (#1A1D26) | 16.1:1 | Pass (AAA) |
| `text-secondary` (#A0A8B8) on `bg-primary` (#0E1117) | 7.9:1 | Pass (AAA) |
| `text-secondary` (#A0A8B8) on `bg-secondary` (#1A1D26) | 7.0:1 | Pass (AAA) |
| `text-tertiary` (#787E8C) on `bg-primary` (#0E1117) | 4.6:1 | Pass (AA) |
| `brand-cyan` (#00D4FF) on `bg-primary` (#0E1117) | 10.7:1 | Pass (AAA) |
| `text-on-accent` (#0E1117) on `brand-cyan` (#00D4FF) | 10.7:1 | Pass (AAA) |
| `error` (#F04848) on `bg-primary` (#0E1117) | 5.2:1 | Pass (AA) |
| `warning` (#FFB020) on `bg-primary` (#0E1117) | 10.3:1 | Pass (AAA) |

### Keyboard Navigation

- All interactive elements must be reachable via Tab key.
- Streamlit widgets handle keyboard navigation natively.
- Chat input should be focusable and submit on Enter.
- Expanders should toggle on Enter/Space when focused.
- Example prompt buttons must be keyboard-accessible (Streamlit buttons are by default).

### Screen Reader Considerations

- Use descriptive labels on all `st.button()` and form widgets.
- Charts should have a `st.caption()` below them describing the data shown.
- Tool call expanders should have descriptive labels (not just "Tool call").
- Use `st.header()` / `st.subheader()` for proper heading hierarchy — do not skip levels.

### Focus Management

- After sending a chat message, focus should return to the chat input.
- Streamlit manages focus for its own widgets. Do not override unless necessary.

### Touch Targets

- Minimum touch target: 44x44px (Streamlit widgets meet this by default).
- Example prompt buttons should be full-width to provide large tap targets on mobile.

---

## Plotly Chart Accessibility

- Always include axis labels and chart titles.
- Use the `hovertemplate` parameter to provide clear data on hover.
- Do not rely on color alone to convey meaning — combine color with labels, patterns, or annotations.
- For candlestick charts, include the direction (up/down) in hover text, not just color.

---

## Branding (Issue #12)

### Logo Usage

- **File**: `logo.jpeg`
- **Sidebar placement**: Display at the top of the sidebar via `st.sidebar.image("logo.jpeg")`.
- **Sizing**: Use `width=200` for sidebar display. The logo is wide-format and works well at this size.
- **Empty state**: Display centered at `width=280` in the main area empty state.
- **Alt text**: "Stegosource — Dynamic Data Agent"

### Brand Voice

- **Technical but approachable.** Explain what the agent is doing, not how.
- **Concise.** Short sentences. No filler words.
- **Confident.** "Here's your chart" not "I hope this helps!"
- **No emoji in agent text.** The logo has enough personality.

---

## Agent-Generated Code Guidelines

When the agent writes code into `app.py`, it should follow these conventions to maintain visual consistency:

1. **Always use `use_container_width=True`** on `st.plotly_chart()`.
2. **Apply the Plotly template** defined above to all chart figures.
3. **Use `type="primary"`** on the main submit button in forms.
4. **Label all form inputs** with clear, concise labels.
5. **Use `st.columns()`** for multi-element layouts, not custom HTML.
6. **Add `st.caption()`** below charts with a data description.
7. **Use semantic status functions** (`st.success`, `st.warning`, `st.error`, `st.info`) for feedback.
8. **Preserve the scaffold section** — never modify the chat interface code.

---

## File Reference

| File | Purpose |
|------|---------|
| `.streamlit/config.toml` | Streamlit theme configuration |
| `app.py` (scaffold CSS block) | CSS custom properties injection |
| `design-system.md` | This document — source of truth for design decisions |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-16 | Initial design system created |
