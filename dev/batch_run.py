#!/usr/bin/env python3
import subprocess
import sys
import time
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: ./batch_run.py <num_iterations>")
        sys.exit(1)

    try:
        num_iterations = int(sys.argv[1])
    except ValueError:
        print("Error: Number of iterations must be an integer.")
        sys.exit(1)
    
    print(f"🎬 Starting batch run of {num_iterations} iterations...")
    overall_start = time.time()

    for i in range(num_iterations):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\n" + "="*60)
        print(f"🚀 [{now}] BATCH ITERATION {i+1} of {num_iterations}")
        print("="*60)
        
        start_time = time.time()
        
        # Run the orchestrator
        # We use ./orchestrator.py directly as it has its own shebang
        try:
            subprocess.run(["./orchestrator.py"], check=False)
        except Exception as e:
            print(f"❌ Error during execution: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ Iteration {i+1} finished in {duration:.2f} seconds.")

    overall_duration = time.time() - overall_start
    print(f"\n" + "🏁" * 30)
    print(f"✨ ALL {num_iterations} ITERATIONS COMPLETE ✨")
    print(f"Total time elapsed: {overall_duration/60:.2f} minutes")
    print("🏁" * 30)

if __name__ == "__main__":
    main()
