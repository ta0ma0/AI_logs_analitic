#!/bin/bash

SCRIPT_PATH="$0"
USER=ruslan

# Получаем абсолютный путь к самому скрипту
ABS_SCRIPT_PATH=$(readlink -f "$SCRIPT_PATH")

# Получаем директорию, содержащую скрипт, из абсолютного пути
SCRIPT_DIR=$(dirname "$ABS_SCRIPT_PATH")

echo "Script directory: $SCRIPT_DIR"

cd "$SCRIPT_DIR" || { echo "Error: Could not change directory to $SCRIPT_DIR"; exit 1; }

./modules/collect_logs.sh

su - $USER -c "
  cd \"$SCRIPT_DIR\" &&
  if [ -f \"venv/bin/activate\" ]; then
    source \"venv/bin/activate\"
    echo \"Virtual environment activated.\"
    if [ -f \"$SCRIPT_DIR/logs_analiser_llama.py\" ]; then
      \"$SCRIPT_DIR/venv/bin/python\" \"$SCRIPT_DIR/logs_analiser_llama.py\"
      result=$?
      deactivate
      echo \"Virtual environment deactivated.\"
      exit $result
    else
      echo \"Error: Python script '$SCRIPT_DIR/logs_analiser_llama.py' not found.\"
      exit 1
    fi
  else
    echo \"Error: Virtual environment activation script '$SCRIPT_DIR/venv/bin/activate' not found.\"
    exit 1
  fi
"