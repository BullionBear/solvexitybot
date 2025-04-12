#!/bin/bash

set -e
set -o pipefail

SCRIPT_NAME="run.sh prod"
CONFIG_YML="config.yml"
CONFIG_PY="bot/config.py"
BOT_MODULE="bot.bot"
LOG_FILE="bot.log"

case "$1" in
  local)
    echo "🔄 Generating $CONFIG_PY from $CONFIG_YML..."
    python yml_to_py.py "$CONFIG_YML" "$CONFIG_PY"

    echo "🚀 Running bot in foreground..."
    python -m "$BOT_MODULE"
    ;;

  prod)
    echo "🔄 Generating $CONFIG_PY from $CONFIG_YML..."
    python yml_to_py.py "$CONFIG_YML" "$CONFIG_PY"

    echo "🚀 Running bot in background (detached)..."
    nohup bash "$0" local > "$LOG_FILE" 2>&1 &
    echo "✅ Bot started in background. Logs: $LOG_FILE"
    ;;

  stop)
    echo "🛑 Stopping production bot..."
    PIDS=$(ps aux | grep "$SCRIPT_NAME" | grep -v grep | awk '{print $2}')
    if [[ -z "$PIDS" ]]; then
      echo "⚠️  No running bot process found."
    else
      echo "🔪 Killing PIDs: $PIDS"
      kill $PIDS
      echo "✅ Stopped."
    fi
    ;;

  *)
    echo "Usage: $0 {local|prod|stop}"
    exit 1
    ;;
esac
