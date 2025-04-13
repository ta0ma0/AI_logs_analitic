#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
echo $SCRIPT_DIR
cd $SCRIPT_DIR
./modules/collect_logs.sh
su - ruslan -c "source $SCRIPT_DIR/venv/bin/activate && python $SCRIPT_DIR/logs_analiser_llama.py"