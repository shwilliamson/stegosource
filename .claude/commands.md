## Project Commands

### Quick Reference

| Action | Command |
|--------|---------|
| Install dependencies | `uv pip install -e ".[dev]" 2>/dev/null \|\| pip install -e ".[dev]"` |
| Start development server | `streamlit run app.py --server.runOnSave=true` |
| Stop development server | `pkill -f "streamlit run"` |
| Run all tests | `pytest` |
| Run E2E tests | Use Playwright MCP (see below) |
| Lint code | `ruff check .` |
| Format code | `ruff format .` |

### Application Lifecycle

```bash
# Install dependencies
uv pip install -e ".[dev]" 2>/dev/null || pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env to add: ANTHROPIC_API_KEY, ALPHAVANTAGE_API_KEY

# Start development server (hot-reloads on file save)
streamlit run app.py --server.runOnSave=true

# App runs at http://localhost:8501

# Stop the server
# Ctrl+C in the terminal, or:
pkill -f "streamlit run"
```

### Hot-Reload

Streamlit auto-reloads when `app.py` is saved (`--server.runOnSave=true`). No manual restart needed for UI changes. Restart required only for:
- Dependency changes (pyproject.toml)
- Streamlit config changes (.streamlit/config.toml)
- Environment variable changes (.env)

### Browser Testing with Playwright MCP

The Tester agent uses the Playwright MCP server for E2E testing. No Playwright CLI installation needed.

```
1. Ensure app is running: streamlit run app.py --server.runOnSave=true &
2. Use Playwright MCP tools:
   - browser_navigate → http://localhost:8501
   - browser_snapshot → get accessibility tree (preferred for interaction)
   - browser_take_screenshot → visual verification
   - browser_click / browser_type → interact with elements
   - browser_wait_for → handle async loading and hot-reloads
   - browser_console_messages → check for JS errors
```

### Git Workflow

```bash
# Create feature branch (follows convention: {issue-num}-{slug})
git checkout -b 42-user-authentication

# Push and create PR
git push -u origin [branch-name]
gh pr create
```

<!-- AUTOMATASAURUS:COMMANDS:START -->
<!-- Managed section preserved for framework compatibility -->
<!-- AUTOMATASAURUS:COMMANDS:END -->
