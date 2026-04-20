#!/usr/bin/env bash

# OLLAMA_NUM_PARALLEL=5 ollama serve -- USE THIS COMMAND TO ALLOW OLLAMA IN PARALLEL

# Arguments
TOTAL_RUNS=${1:-100}
CONCURRENCY=${2:-4}

echo "🌀 Starting $TOTAL_RUNS total agent sessions across $CONCURRENCY parallel workers..."
echo "Logs will be written to logs/agent_run_N.log"

# Create a logs directory to keep the root directory clean
mkdir -p logs

# Use xargs to manage the process pool:
# - seq generates numbers 1 to TOTAL_RUNS
# - xargs -P specifies the maximum number of concurrent processes
# -I {} replaces {} with the run number
seq 1 "$TOTAL_RUNS" | xargs -I {} -P "$CONCURRENCY" bash -c '
    echo "▶️ Spawning Run {}..."
    ./agent_runner.py > "logs/agent_run_{}.log" 2>&1
    echo "✅ Completed Run {}"
'

echo "🏁 All $TOTAL_RUNS runs completed! Check the logs/ folder for individual run outputs."
