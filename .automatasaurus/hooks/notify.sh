#!/bin/bash
# Automatasaurus Notification Hook
# Sends desktop notifications and optional sound alerts

# Configuration
SOUND_ENABLED="${AUTOMATASAURUS_SOUND:-true}"
SOUND_FILE="/System/Library/Sounds/Glass.aiff"

# Parse arguments
TITLE="${1:-Automatasaurus}"
MESSAGE="${2:-Notification}"
TYPE="${3:-info}"  # info, question, approval, stuck, complete

# Set icon/subtitle based on type
case "$TYPE" in
  question)
    SUBTITLE="Question Needs Answer"
    SOUND_FILE="/System/Library/Sounds/Submarine.aiff"
    ;;
  approval)
    SUBTITLE="Approval Required"
    SOUND_FILE="/System/Library/Sounds/Submarine.aiff"
    ;;
  stuck)
    SUBTITLE="Agent Needs Help"
    SOUND_FILE="/System/Library/Sounds/Basso.aiff"
    ;;
  complete)
    SUBTITLE="Work Complete"
    SOUND_FILE="/System/Library/Sounds/Hero.aiff"
    ;;
  handoff)
    SUBTITLE="Task Handed Off"
    SOUND_FILE="/System/Library/Sounds/Pop.aiff"
    ;;
  progress)
    SUBTITLE="Work Continuing"
    SOUND_FILE="/System/Library/Sounds/Tink.aiff"
    ;;
  error)
    SUBTITLE="Error Occurred"
    SOUND_FILE="/System/Library/Sounds/Basso.aiff"
    ;;
  *)
    SUBTITLE="Info"
    SOUND_FILE="/System/Library/Sounds/Glass.aiff"
    ;;
esac

# Detect OS and send notification
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e "display notification \"$MESSAGE\" with title \"$TITLE\" subtitle \"$SUBTITLE\""

  # Play sound if enabled
  if [[ "$SOUND_ENABLED" == "true" ]] && [[ -f "$SOUND_FILE" ]]; then
    afplay "$SOUND_FILE" &
  fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux with notify-send
  if command -v notify-send &> /dev/null; then
    notify-send "$TITLE" "$MESSAGE" --urgency=normal
  fi

  # Play sound if enabled (requires paplay or aplay)
  if [[ "$SOUND_ENABLED" == "true" ]]; then
    if command -v paplay &> /dev/null; then
      paplay /usr/share/sounds/freedesktop/stereo/message.oga &
    fi
  fi

elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
  # Windows (Git Bash / Cygwin)
  if command -v powershell &> /dev/null; then
    powershell -Command "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('$MESSAGE', '$TITLE')"
  fi
fi

# Log the notification
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$TYPE] $TITLE: $MESSAGE" >> "${AUTOMATASAURUS_LOG:-/tmp/automatasaurus.log}"

exit 0