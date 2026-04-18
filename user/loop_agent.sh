#!/usr/bin/env bash

# Default to 5 iterations if no number is provided
NUM_RUNS=${1:-5}

echo "🌀 Starting Agent Runner loop for $NUM_RUNS iterations..."

for (( i=1; i<=NUM_RUNS; i++ ))
do
    echo "======================================"
    echo "🤖 AGENT RUN $i of $NUM_RUNS"
    echo "======================================"
    
    ./agent_runner.py
    
    # Optional: Brief cooldown between autonomous agent sessions
    echo "⏲️  Cooling down for 3 seconds..."
    sleep 3
done

echo "✅ Agent Runner batch completion finished!"
