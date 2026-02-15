#!/bin/bash
# Automatasaurus Request Attention Hook
# Agents can call this explicitly when they need user attention

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFY="$SCRIPT_DIR/notify.sh"

# Usage: request-attention.sh <type> <message>
# Types: question, approval, stuck, complete, handoff, progress, info

TYPE="${1:-info}"
MESSAGE="${2:-Your attention is needed}"

"$NOTIFY" "Automatasaurus" "$MESSAGE" "$TYPE"

exit 0