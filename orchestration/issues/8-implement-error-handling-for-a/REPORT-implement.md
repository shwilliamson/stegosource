# Agent Report: implement
Completed: 2026-02-16

## Summary
Implemented comprehensive error handling for API limits, bad input, and agent failures as specified in issue #8.

## Changes Made

### 1. `app.py` — Persistent API key banners
- Added `import os` to enable environment variable checks
- Added persistent `st.error()` banner when `ANTHROPIC_API_KEY` is not set, explaining the agent cannot function
- Added persistent `st.warning()` banner when `ALPHAVANTAGE_API_KEY` is not set, explaining data features are unavailable
- Both banners appear between the sidebar and dynamic sections, so they are always visible in the main area regardless of what the agent puts in the dynamic section

### 2. `agent.py` — System prompt error handling instructions
- Added a new "## Error Handling" section with specific guidance for each error type:
  - `InvalidTickerError`: respond with helpful message and suggestions
  - `RateLimitError`: use `st.toast()` for transient notification
  - `MissingApiKeyError`: use `st.warning()` for persistent banner
  - `ApiError`: report gracefully in chat
- Added "### Error Handling Pattern" with a code example using specific exception types
- Added "### Code Quality" checklist for mental validation before saving
- Updated all chart examples (line, candlestick, multi-symbol) to use specific exception types instead of bare `except Exception`

### 3. `tests/test_agent.py` — New system prompt tests
- `test_contains_error_handling_section`: verifies Error Handling section exists
- `test_contains_invalid_ticker_guidance`: verifies InvalidTickerError guidance
- `test_contains_rate_limit_toast_guidance`: verifies st.toast usage guidance
- `test_contains_missing_api_key_guidance`: verifies MissingApiKeyError guidance
- `test_contains_network_error_guidance`: verifies ApiError/network guidance
- `test_contains_code_quality_section`: verifies code quality checklist
- `test_contains_specific_exception_imports`: verifies specific exception import pattern
- Updated `test_contains_error_handling_pattern` to check for specific exception types

### 4. `tests/test_app.py` — New API key banner tests
- `test_app_imports_os`: verifies os import
- `test_anthropic_key_check_in_scaffold`: verifies Anthropic key check exists
- `test_alphavantage_key_check_in_scaffold`: verifies Alpha Vantage key check exists
- `test_anthropic_key_uses_st_error`: verifies st.error for Anthropic key
- `test_alphavantage_key_uses_st_warning`: verifies st.warning for Alpha Vantage key
- `test_api_key_checks_before_dynamic_section`: verifies placement order
- `test_api_key_checks_after_sidebar`: verifies placement after sidebar

## Acceptance Criteria Coverage
| Criterion | How Addressed |
|-----------|---------------|
| Invalid ticker: helpful chat message | System prompt instructs agent to catch `InvalidTickerError` and suggest alternatives |
| Rate limit: `st.toast()` notification | System prompt and all examples use `st.toast()` for rate limits |
| Missing AV API key: `st.warning()` | Persistent `st.warning()` at app startup + system prompt pattern |
| Missing Anthropic key: `st.error()` | Persistent `st.error()` at app startup + existing AgentConfigError handler |
| Network errors: graceful chat handling | System prompt instructs agent to catch `ApiError` with user-friendly messages |
| Broken code recovery | Streamlit shows Python errors by default; system prompt has Code Quality checklist for prevention |

## Test Results
- All 201 tests pass
- Linting passes (ruff check)
- Formatting passes (ruff format)

## Decisions
- Placed API key checks between scaffold end and dynamic start, outside both sections, so they persist regardless of agent modifications to the dynamic section
- Chose NOT to wrap the dynamic section in try/except because: (1) Streamlit already shows errors in the UI, (2) wrapping would break the agent's ability to define functions at module level, (3) the Code Quality checklist in the system prompt is the better prevention mechanism
- Used specific exception types in all examples rather than bare `except Exception` — this teaches the agent to handle each error type differently
