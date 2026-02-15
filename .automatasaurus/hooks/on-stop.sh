#!/bin/bash
# Automatasaurus Stop Hook
# Called when Claude finishes a response

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFY="$SCRIPT_DIR/notify.sh"

# Read the stop context from stdin (passed by Claude Code)
CONTEXT=$(cat)

# Check if this looks like a completion, handoff, question, or stuck state
# The context contains Claude's last response
# Order matters - check more specific patterns first

# Handoff: subagent completed, passing to next agent (no notification - silent)
if echo "$CONTEXT" | grep -qi "handing off to\|passing to\|next agent\|handoff complete\|task handed\|routing to\|subagent complete\|agent will take over"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Subagent handoff (silent)" >> "${AUTOMATASAURUS_LOG:-/tmp/automatasaurus.log}"
  exit 0
fi

# Work continuing: orchestration is progressing (no notification - silent)
if echo "$CONTEXT" | grep -qi "continuing with\|moving on to\|proceeding to\|next step\|processing issue\|starting work on"; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Workflow progressing (silent)" >> "${AUTOMATASAURUS_LOG:-/tmp/automatasaurus.log}"
  exit 0
fi

# Fully complete: all work done, nothing more to do
if echo "$CONTEXT" | grep -qi "all issues complete\|workflow complete\|no more issues\|all tasks complete\|finished processing"; then
  "$NOTIFY" "Automatasaurus" "All work complete" "complete"
  exit 0
fi

# Stuck/Error: agent hit a blocker (needs human help)
if echo "$CONTEXT" | grep -qi "stuck\|blocked\|cannot proceed\|unable to continue\|failed after\|escalating to human\|need human"; then
  "$NOTIFY" "Automatasaurus" "Agent needs help" "stuck"
  exit 0
fi

# Question: explicit question for user (not rhetorical)
if echo "$CONTEXT" | grep -qi "need your input\|please choose\|which option would you\|waiting for your\|your decision on"; then
  "$NOTIFY" "Automatasaurus" "Question needs your answer" "question"
  exit 0
fi

# Approval: explicit approval request (permission to proceed)
if echo "$CONTEXT" | grep -qi "awaiting your approval\|please approve\|need your permission\|authorize this\|confirm to proceed"; then
  "$NOTIFY" "Automatasaurus" "Approval required" "approval"
  exit 0
fi

# Default: just log that we stopped (no notification - routine stop)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Agent stopped (routine)" >> "${AUTOMATASAURUS_LOG:-/tmp/automatasaurus.log}"

exit 0