#!/usr/bin/env bash

# Default to 5 iterations if no number is provided
NUM_RUNS=${1:-5}

echo "🌀 Starting batch generation for $NUM_RUNS iterations..."

for (( i=1; i<=NUM_RUNS; i++ ))
do
    echo "======================================"
    echo "🚀 RUN $i of $NUM_RUNS"
    echo "======================================"
    
    ./generate.py
    
    # Optional: Add a brief 5-second sleep to ensure we stay well under Gemini API rate limits
    echo "⏲️  Cooling down for 5 seconds..."
    sleep 5
done

echo "✅ Batch completion finished!"
