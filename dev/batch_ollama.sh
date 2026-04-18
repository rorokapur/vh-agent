#!/usr/bin/env bash

# Default to 5 iterations if no number is provided
NUM_RUNS=${1:-5}

echo "🌀 Starting Ollama batch generation for $NUM_RUNS iterations..."

for (( i=1; i<=NUM_RUNS; i++ ))
do
    echo "======================================"
    echo "🚀 RUN $i of $NUM_RUNS (Local Ollama)"
    echo "======================================"
    
    ./generate_ollama.py
    
    # Optional: Brief local cooldown
    echo "⏲️  Cooling down for 3 seconds..."
    sleep 3
done

echo "✅ Ollama Batch completion finished!"
