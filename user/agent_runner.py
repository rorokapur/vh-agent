#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "ollama",
# ]
# ///

import requests
import random
import time
import sys
import json
import os
import tempfile
import ollama

# Explicitly bind to IPv4 to bypass a common macOS httpx IPv6 'localhost' timeout
ollama_client = ollama.Client(host='http://127.0.0.1:11434')

BASE_URL = "https://staging.visual-honesty.rohankapur.dev"
MODEL_NAME = "gemma4:e2b"
MAX_STREAM_TIME = 60.0

class Colors:
    CYAN = '\033[96m'
    DIM = '\033[2m'
    ENDC = '\033[0m'

class SolverAgent:
    def __init__(self):
        self.session_id = None
        self.requests_session = requests.Session()

    def handle_error(self, response):
        """Prints robust error info, specifically response.text for 500s."""
        if response.status_code >= 500:
            print(f"!!! SERVER ERROR {response.status_code} !!!")
            print("Response Text (PostgreSQL/Debug Info):")
            print(response.text)
        else:
            print(f"Error {response.status_code}: {response.text}")

    def initialize_session(self):
        print("Initializing session...")
        payload = {
            "p_category": "ai",
            "p_demographics": {"type": MODEL_NAME}
        }
        try:
            response = self.requests_session.post(f"{BASE_URL}/api/user/", json=payload)
            if response.status_code == 200 or response.status_code == 201:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        self.session_id = data.get("id")
                    else:
                        # Sometimes the server returns the ID as a direct JSON string
                        self.session_id = str(data)
                except Exception:
                    # Fallback to raw text if JSON parsing fails
                    self.session_id = response.text.strip().strip('"')

                if not self.session_id:
                    print(f"Error: Could not find ID in response. Text: {response.text}")
                    return False

                print(f"Session initialized successfully. ID: {self.session_id}")
                self.requests_session.headers.update({"X-Session-ID": str(self.session_id)})
                return True
            else:
                self.handle_error(response)
                return False
        except Exception as e:
            print(f"Request failed: {e}")
            return False

    def get_next_trial(self):
        print("\nFetching next trial...")
        try:
            response = self.requests_session.get(f"{BASE_URL}/api/user/trial/next")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print("No more trials available.")
                return None
            else:
                self.handle_error(response)
                return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def analyze_image(self, trial_data):
        """Processes comparative task: downloads images from left/right paths and queries Llama 3.2 Vision."""
        left = trial_data.get("left", {})
        right = trial_data.get("right", {})
        
        left_id = left.get("id")
        right_id = right.get("id")
        
        if not left_id or not right_id:
            print("Error: Trial data missing 'left' or 'right' IDs.")
            return None, 0

        l_url = f"{BASE_URL}{left.get('image_url')}"
        r_url = f"{BASE_URL}{right.get('image_url')}"

        print(f"Layout: Left={left_id[:8]}, Right={right_id[:8]}")

        start_time = time.time()
        with tempfile.TemporaryDirectory() as tmpdir:
            l_file = os.path.join(tmpdir, "left.png")
            r_file = os.path.join(tmpdir, "right.png")
            
            try:
                # Download
                with open(l_file, "wb") as f:
                    f.write(self.requests_session.get(l_url).content)
                with open(r_file, "wb") as f:
                    f.write(self.requests_session.get(r_url).content)

                # Prompt Llama via Ollama
                prompt = (
                    'I am showing you two charts. The first image provided is the "Left" chart, and the '
                    'second image provided is the "Right" chart. One is a standard, honest visualization, '
                    'and the other uses a deceptive tactic (like a truncated axis or skewed scaling) to '
                    'misrepresent the data. Which one is deceptive? If you cannot definitively conclude '
                    'which one is strictly deceptive, choose the one that could more easily be used '
                    'to deceive a viewer. You MUST respond EXACTLY and ONLY with either "Left" or "Right". '
                    'Do not include any other text, explanation, or punctuation.'
                )
                
                trial_start = time.time()
                attempt = 0
                choice_id = None
                
                while True:
                    attempt += 1
                    print(f"Querying {MODEL_NAME} (Ollama) [Attempt {attempt}]...")
                    
                    req_start = time.time()
                    stream = ollama_client.chat(
                        model=MODEL_NAME,
                        messages=[{
                            'role': 'user',
                            'content': prompt,
                            'images': [l_file, r_file]
                        }],
                        think=True,
                        stream=True
                    )
                    
                    model_output = ""
                    in_thinking = False
                    first_token_received = False
                    generation_start = 0.0
                    stream_aborted = False
                    
                    for chunk in stream:
                        if not first_token_received:
                            ttft = time.time() - req_start
                            print(f"[TTFT: {ttft:.2f}s] ", end="")
                            first_token_received = True

                        # Enforce total trial overarching cutoff
                        if (time.time() - trial_start) > MAX_STREAM_TIME:
                            print(f"\n[ERROR] Total execution time exceeded {MAX_STREAM_TIME}s limit! Aborting stream.")
                            stream_aborted = True
                            break

                        # 1. Handle the reasoning/thinking trace
                        if getattr(chunk.message, 'thinking', None):
                            if not in_thinking:
                                print(f'\n{Colors.DIM}--- Thinking ---\n', end='')
                                in_thinking = True
                            print(chunk.message.thinking, end='', flush=True)

                        # 2. Handle the final answer
                        elif getattr(chunk.message, 'content', None):
                            if in_thinking:
                                print(f'{Colors.ENDC}\n\n{Colors.CYAN}--- Final Answer ---\n', end='')
                                in_thinking = False
                            elif not model_output:
                                print(f'\n{Colors.CYAN}--- Final Answer ---\n', end='')
                                
                            print(chunk.message.content, end='', flush=True)
                            model_output += chunk.message.content
                            
                    print(f'{Colors.ENDC}\n')  # Add a final newline when done
                        
                    if stream_aborted:
                        # If we timed out, gracefully return None to the server
                        choice_id = None
                        break
                    
                    model_output = model_output.strip()
                    answer = model_output.lower()
                    
                    # Use robust rfind logic since the prompt asks for step-by-step reasoning before concluding
                    left_idx = answer.rfind("left")
                    right_idx = answer.rfind("right")
                    
                    if left_idx == -1 and right_idx == -1:
                        # Enforce total trial overarching cutoff before triggering another retry
                        if (time.time() - trial_start) > MAX_STREAM_TIME:
                            print(f"\n[ERROR] Ambiguous output and trial time exceeded {MAX_STREAM_TIME}s limit! Submitting null.")
                            choice_id = None
                            break
                            
                        print(f"Warning: Ambiguous model output (or empty response). Retrying...")
                        print(f"[DEBUG] Model Output computed was: '{model_output}'")
                        print(f"[DEBUG] Total Trial Elapsed Time: {time.time() - trial_start:.2f}s / {MAX_STREAM_TIME}s")
                        continue  # Let the while true loop retry!
                    elif left_idx > right_idx:
                        choice_id = left_id
                        break
                    else:
                        choice_id = right_id
                        break
                
            except Exception as e:
                print(f"Analysis failed: {e}")
                choice_id = None

            analysis_time_ms = int((time.time() - start_time) * 1000)
            return choice_id, analysis_time_ms

    def submit_trial(self, trial_id, choice, analysis_time):
        print(f"Submitting trial {trial_id}: choice={choice} (Time elapsed: {analysis_time/1000.0:.2f}s)")
        payload = {
            "trialId": trial_id,
            "choice": choice,
            "frontendTime": analysis_time
        }
        try:
            response = self.requests_session.post(f"{BASE_URL}/api/user/trial/submit", json=payload)
            if response.status_code == 200 or response.status_code == 201:
                print("Submission successful.")
                return True
            else:
                self.handle_error(response)
                return False
        except Exception as e:
            print(f"Request failed: {e}")
            return False

    def get_results_summary(self):
        print("\nFetching results summary...")
        try:
            response = self.requests_session.get(f"{BASE_URL}/api/user/results/summary")
            if response.status_code == 200:
                return response.json()
            else:
                self.handle_error(response)
                return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_results_categories(self):
        print("Fetching categorical results...")
        try:
            response = self.requests_session.get(f"{BASE_URL}/api/user/results/categories")
            if response.status_code == 200:
                return response.json()
            else:
                self.handle_error(response)
                return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

def main():
    agent = SolverAgent()
    
    if not agent.initialize_session():
        print("Failed to initialize session. Exiting.")
        sys.exit(1)

    trials_conducted = 0
    # The agent will now run until all trials are exhausted
    while True:
        trial_data = agent.get_next_trial()
        if not trial_data:
            break
            
        # Check if we've exhausted all available sets
        if isinstance(trial_data, dict) and trial_data.get("sets_remaining") == 0:
            print("All trial sets exhausted.")
            break

        trial_id = None
        if isinstance(trial_data, dict):
            # API returns 'trial_id' based on the SQL function
            trial_id = trial_data.get("trial_id") or trial_data.get("id")
        else:
            # Fallback if trial_data is just the ID string
            trial_id = str(trial_data)

        if not trial_id:
            print(f"Error: Could not extract trial ID from response: {trial_data}")
            break

        choice_id, analysis_time = agent.analyze_image(trial_data)
        
        if agent.submit_trial(trial_id, choice_id, analysis_time):
            trials_conducted += 1
            print(f"Progress: {trials_conducted} trials completed.")
            
            # Fetch stats immediately to trigger the backend upsert pattern
            _ = agent.get_results_summary()
            print("[Sync] Fetched results to upsert latest stats in backend.")
        else:
            print("Failed to submit trial. Retrying sequence...")
            # We don't increment trials_conducted if submission failed
            time.sleep(1)

    print(f"\nSimulation complete. {trials_conducted} trials processed.")

    # Fetch final stats
    summary = agent.get_results_summary()
    if summary:
        print("\n--- Participant Summary ---")
        print(json.dumps(summary, indent=2))
        
    categories = agent.get_results_categories()
    if categories:
        print("\n--- Categorical Comparison ---")
        print(json.dumps(categories, indent=2))

if __name__ == "__main__":
    main()
