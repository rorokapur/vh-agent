#!/usr/bin/env -S uv run

import os
import sys
import re
import datetime
import subprocess
from pathlib import Path
import random

MAX_STRATEGY_REVISIONS = 2
MAX_STRATEGY_RETRIES = 3
MAX_CODE_RETRIES = 3
MAX_CODE_REVISIONS = 3
MAX_EVALUATOR_RETRIES = 3

GEMINI_MODEL = "gemini-3.1-pro-preview"
OLLAMA_MODEL = "gemma4:26b"

def evaluate_chart_with_history(strategy_text, code_text, image_paths, claim_a, claim_b, log_path="evaluator_log.txt"):
    import ollama  # type: ignore
    import re
    
    for attempt in range(MAX_EVALUATOR_RETRIES):
        chat_history = [
            {'role': 'system', 'content': 'You are a precise Data Visualization Reviewer. You analyze charts for visual honesty and provide technical feedback on Python code.'}
        ]
        
        def save_log():
            with open(log_path, "w", encoding='utf-8') as f:
                for turn in chat_history:
                    role = turn.get('role', 'unknown').upper()
                    content = turn.get('content', '')
                    f.write(f"=== {role} ===\n{content}\n\n")
        
        # Turn 1: Blind Analysis & Incoherence Filter
        prompt_1 = f"You are an expert Data Visualization Reviewer. Look at the two provided chart images (the first attached is Image 1, the second is Image 2).\n\nTwo claims have been written about these charts (one is honest, one is deceptive):\n- Claim A: {claim_a}\n- Claim B: {claim_b}\n\nTask:\n1. Figure out which image goes with which claim.\n2. Evaluate if there is successful visual deception. True deception is subtle and misleading. Incoherence (unreadable text, overlapping elements, broken axes, or obvious glitches) is NOT true deception, it is just a broken chart.\n\nBased on a 3-second glance, is one of the charts successfully and subtly deceptive? Or is it just honest, or perhaps incoherent/glitchy?"
        chat_history.append({'role': 'user', 'content': prompt_1, 'images': image_paths})
        
        print("      > Turn 1: Blind Analysis & Incoherence Check...")
        response_1 = ollama.chat(model=OLLAMA_MODEL, messages=chat_history)
        chat_history.append(response_1.get('message', getattr(response_1, 'message', {})))
        
        # Turn 2: Idea / Strategy Evaluation
        prompt_2 = f"Now, here is the intended deceptive strategy (the idea) that was supposed to guide the chart's creation:\n\n=== STRATEGY ===\n{strategy_text}\n================\n\nTask:\n1. Does the strategy actually match what is visually present in the images? If the code generated charts that have nothing to do with the requested strategy, that is an EXECUTION ISSUE.\n2. If you already determined in Turn 1 that the chart was successfully deceptive and matches the strategy, acknowledge that the idea worked.\n3. However, if the chart was NOT deceptive (e.g., it was honest, or it was incoherent/glitchy), evaluate this strategy. Is the idea itself fundamentally flawed, impossible, or inherently not deceptive? If the idea is bad, state that this is an IDEA ISSUE. If the idea is actually good and viable but the execution was just poor, state that it is an EXECUTION ISSUE.\n\nCRITICAL: You must end your response with EXACTLY ONE of these tags:\n[IDEA WORKED] - if the chart is successfully deceptive and matches the strategy.\n[IDEA ISSUE] - if the strategy is fundamentally flawed.\n[EXECUTION ISSUE] - if the strategy is good but the execution/code failed to deceive."
        chat_history.append({'role': 'user', 'content': prompt_2})
        
        print("      > Turn 2: Idea Evaluation & Strategy Alignment...")
        response_2 = ollama.chat(model=OLLAMA_MODEL, messages=chat_history)
        chat_history.append(response_2.get('message', getattr(response_2, 'message', {})))
        
        turn_2_text = response_2.get('message', {}).get('content', '').upper()
        if "[IDEA WORKED]" in turn_2_text:
            save_log()
            return "PASS"
        elif "[IDEA ISSUE]" in turn_2_text:
            save_log()
            reason = response_2.get('message', {}).get('content', '')
            return f"STRATEGY_ERROR: {reason}"
        elif "[EXECUTION ISSUE]" not in turn_2_text:
            print(f"      > Evaluator formatting failed, retrying evaluation ({attempt + 1}/{MAX_EVALUATOR_RETRIES})...")
            continue
        
        # Turn 3: Code Evaluation & Final Verdict
        prompt_3 = f"The Python script below generated the charts. It failed to achieve the deceptive effect you expected.\n\n=== PYTHON SCRIPT ===\n{code_text}\n\nTask: Identify the bug in this script that prevented the visual deception from working, and provide specific instructions on how to fix it."
        chat_history.append({'role': 'user', 'content': prompt_3})
        
        print("      > Turn 3: Final Verdict (Code Fixes)...")
        response_3 = ollama.chat(model=OLLAMA_MODEL, messages=chat_history)
        chat_history.append(response_3.get('message', getattr(response_3, 'message', {})))
        
        save_log()
        
        final_output = getattr(response_3.message, 'content', '') if hasattr(response_3, 'message') else response_3.get('message', {}).get('content', '')
        
        return f"CODE_ERROR: {final_output.strip()}"
        
    print(f"❌ Evaluator failed to output a valid tag format after {MAX_EVALUATOR_RETRIES} retries. Giving up.")
    sys.exit(1)

def main():
    original_cwd = os.getcwd()
    
    # Default to the deception taxonomy taxonomy
    topic_path = "prompts/deception_taxonomy.md"
    # If an argument is provided, treat it as extra instructions
    extra_instructions = sys.argv[1] if len(sys.argv) > 1 else ""

    system_file = "prompts/system.md"

    categories = ["Statistics", "Encoding", "Container", "Styling"]
    formats = ["Heatmap", "Waterfall Chart", "Violin Plot", "Lollipop Chart", "Radar Chart", "Slope Graph", "Hexbin Plot", "Bubble Chart", "Treemap", "Density Plot", "Mosaic Plot", "Standard Bar Chart", "Standard Line Chart", "Scatter Plot", "Pie Chart"]

    if os.path.isfile(topic_path):
        print(f"🎯 Reading prompt from file: {topic_path}")
        with open(topic_path, 'r', encoding='utf-8') as f:
            topic_text = f.read()
        
        basename = os.path.basename(topic_path)
        name_without_ext = os.path.splitext(basename)[0]
        safe_topic = re.sub(r'[^a-zA-Z0-9\-_]', '', name_without_ext).lower()[:20]
    else:
        print(f"🎯 Topic specified: {topic_path}")
        topic_text = topic_path
        safe_topic = re.sub(r'[^a-zA-Z0-9 \-_]', '', topic_path).replace(' ', '_').lower()[:20]

    # 1. Verify system file exists
    if not os.path.isfile(system_file):
        print(f"❌ Error: System prompt {system_file} not found.")
        sys.exit(1)

    system_path = Path(system_file).resolve()
    idea_generator_path = Path("prompts/idea_generator.md").resolve()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    target_category = random.choice(categories)
    target_format = random.choice(formats)
    print(f"🎲 Randomly assigned deception category: {target_category}")
    print(f"🎲 Randomly assigned chart format: {target_format}")
    
    with open(idea_generator_path, 'r', encoding='utf-8') as f:
        idea_prompt = f.read()
    
    idea_prompt = idea_prompt.replace("{{TARGET_CATEGORY}}", target_category)
    idea_prompt = idea_prompt.replace("{{TARGET_FORMAT}}", target_format)
    
    # Initialize state for the Idea Agent
    idea_history = f"{idea_prompt}\n\n**PROMPT/TOPIC:**\n{topic_text}"

    with open(system_path, 'r', encoding='utf-8') as f:
        system_text = f.read()

    overall_pass = False
    file_prefix = ""
    target_category_saved = target_category
    workspace = ""

    # Outer Loop (Strategy)
    for strategy_revision in range(MAX_STRATEGY_REVISIONS):
        if overall_pass:
            break
            
        # Inner Loop (Strategy Formatting)
        for strategy_attempt in range(MAX_STRATEGY_RETRIES):
            print(f"\n🧠 STEP 1: Consulting Gemini for idea generation (Revision {strategy_revision + 1}/{MAX_STRATEGY_REVISIONS}, Attempt {strategy_attempt + 1}/{MAX_STRATEGY_RETRIES})...")
            
            result = subprocess.run(
                ["gemini", "-m", GEMINI_MODEL],
                input=idea_history.encode('utf-8'),
                capture_output=True,
                check=True
            )
            content = result.stdout.decode('utf-8').strip()
            
            required_keys = ["category_slug:", "context_slug:", "true_claim:", "biased_claim:"]
            missing_keys = [k for k in required_keys if k not in content]
            
            if missing_keys:
                print(f"⚠️ Strategy missing required fields: {', '.join(missing_keys)}. Retrying...")
                idea_history += f"\n\n--- PREVIOUS ATTEMPT FAILED FORMATTING ---\nMissing keys: {', '.join(missing_keys)}\nPlease ensure all required fields are present in your output."
                continue
            else:
                break
        else:
            print(f"\n❌ Strategy generator failed to format output {MAX_STRATEGY_RETRIES} times consecutively. Giving up completely.")
            sys.exit(1)
            
        # Natively strip any "chain of thought" or conversational preamble Gemini outputs
        if "category_slug:" in content:
            content = "category_slug:" + content.split("category_slug:", 1)[1]

        category_slug = "unknown"
        context_slug = "unknown"
        cat_match = re.search(r"category_slug:\s*([a-zA-Z0-9_\-]+)", content)
        if cat_match: category_slug = cat_match.group(1).lower()
        ctx_match = re.search(r"context_slug:\s*([a-zA-Z0-9_\-]+)", content)
        if ctx_match: context_slug = ctx_match.group(1).lower()

        if not workspace:
            file_prefix = f"{category_slug}_{context_slug}_{date_str}"
            os.chdir(original_cwd)
            workspace = os.path.join(original_cwd, f"output/{file_prefix}_{timestamp}")
            os.makedirs(workspace, exist_ok=True)
            os.chdir(workspace)
            print(f"🚀 Workspace created: {workspace}")

        if extra_instructions:
            print(f"📝 Manual instructions: {extra_instructions}")

        with open("strategy.txt", "w", encoding='utf-8') as out_f:
            out_f.write(content)

        print("📝 Strategy generated and saved to strategy.txt.")

        # Initialize state for the Code Agent
        code_history = ""

        # Inner Loop (Evaluator Revisions)
        for code_revision in range(MAX_CODE_REVISIONS):
            run_success = False
            images_exist = False
            
            for code_attempt in range(MAX_CODE_RETRIES):
                print(f"\n🧠 STEP 2: Consulting Gemini for Code Execution (Revision {code_revision + 1}/{MAX_CODE_REVISIONS}, Attempt {code_attempt + 1}/{MAX_CODE_RETRIES})...")
            
                merged_text = f"{system_text}\n{content}"
                merged_text = merged_text.replace("{{FILE_PREFIX}}", file_prefix)
    
                if extra_instructions:
                    merged_text += f"\n\n**MANUAL INSTRUCTIONS:**\n{extra_instructions}"
    
                if code_history:
                    gemini_code_input = f"{merged_text}\n\n{code_history}"
                else:
                    gemini_code_input = merged_text
    
                with open("script.py", "w", encoding='utf-8') as out_f:
                    subprocess.run(
                        ["gemini", "-m", GEMINI_MODEL],
                        input=gemini_code_input.encode('utf-8'),
                        stdout=out_f,
                        check=True
                    )
                
                with open("script.py", "r", encoding='utf-8') as in_f:
                    generated_code = in_f.read()
    
                print("📊 Rendering charts...")
                execution_output = ""
                run_success = False
                for auto_install_attempt in range(3):
                    run_result = subprocess.run(["uv", "run", "script.py"], capture_output=True, text=True)
                    execution_output = f"STDOUT:\n{run_result.stdout}\nSTDERR:\n{run_result.stderr}"
                    
                    if run_result.returncode == 0:
                        run_success = True
                        break
                    
                    match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", run_result.stderr)
                    if match:
                        missing_module = match.group(1)
                        print(f"📦 Auto-installing missing module '{missing_module}'...")
                        subprocess.run(["uv", "pip", "install", missing_module], check=True)
                        print("🔄 Retrying script execution...")
                    else:
                        print(f"⚠️ Script execution failed:\n{run_result.stderr}")
                        break
    
                honest_png = f"{file_prefix}_honest.png"
                deceptive_png = f"{file_prefix}_deceptive.png"
                
                images_exist = os.path.exists(honest_png) and os.path.exists(deceptive_png)
                
                if not run_success or not images_exist:
                    print("❌ Code execution failed or images not generated.")
                    error_msg = execution_output if not run_success else "Images not found after execution."
                    code_history += f"\n\n--- PREVIOUS ATTEMPT FAILED ---\nCode:\n{generated_code}\nExecution Output:\n{error_msg}\nPlease fix the errors and provide ONLY the raw, working python code."
                    continue
                else:
                    break
                    
            else:
                print(f"\n❌ Code generator failed to produce running code {MAX_CODE_RETRIES} times consecutively. Giving up completely.")
                sys.exit(1)
                
            if True:
                honest_txt = f"{file_prefix}_honest.txt"
                deceptive_txt = f"{file_prefix}_deceptive.txt"
                
                try:
                    with open(honest_txt, 'r', encoding='utf-8') as f:
                        honest_claim = f.read().strip()
                    with open(deceptive_txt, 'r', encoding='utf-8') as f:
                        deceptive_claim = f.read().strip()
                except Exception as e:
                    print(f"⚠️ Failed to read claim text files: {e}")
                    honest_claim = "Honest claim missing"
                    deceptive_claim = "Deceptive claim missing"
    
                claims = [honest_claim, deceptive_claim]
                random.shuffle(claims)
                claim_a, claim_b = claims[0], claims[1]
                
                image_paths = [honest_png, deceptive_png]
                random.shuffle(image_paths)
    
                print("👁️  Calling Evaluator Agent (gemma4:e2b) via 3-Turn Chat...")
                # We pass both image paths (shuffled) and claims (shuffled) for blinded analysis
                evaluator_output = evaluate_chart_with_history(content, generated_code, image_paths, claim_a, claim_b, "evaluator_log.txt")
                print(f"⚖️  Evaluator Output:\n{evaluator_output}")
    
                # Archiving helper function
                def archive_files(strategy_idx, revision_idx, move_strategy=False):
                    import shutil
                    archive_dir = os.path.join(workspace, "archive", f"s{strategy_idx}_r{revision_idx}")
                    os.makedirs(archive_dir, exist_ok=True)
                    for f in os.listdir("."):
                        if os.path.isfile(f):
                            if f == "strategy.txt" and not move_strategy:
                                continue
                            shutil.move(f, os.path.join(archive_dir, f))
        
                # Routing Logic based on Evaluator Output
                evaluator_output_upper = evaluator_output.strip().upper()
                if evaluator_output_upper.startswith("PASS") or "PASS\n" in evaluator_output_upper or evaluator_output_upper == "PASS":
                    overall_pass = True
                    break # Break code loop
                elif "STRATEGY_ERROR" in evaluator_output:
                    reason = evaluator_output.split("STRATEGY_ERROR", 1)[-1].lstrip(":- \n")
                    idea_history += f"\n\n--- PREVIOUS ATTEMPT FAILED ---\nStrategy:\n{content}\nEvaluator Feedback:\n{reason}\nPlease provide a fundamentally different and improved strategy."
                    archive_files(strategy_revision, code_revision, move_strategy=True)
                    break # Break code loop and retry strategy loop
                elif "CODE_ERROR" in evaluator_output:
                    reason = evaluator_output.split("CODE_ERROR", 1)[-1].lstrip(":- \n")
                    code_history += f"\n\n--- PREVIOUS ATTEMPT FAILED ---\nCode:\n{generated_code}\nExecution Output:\n{execution_output}\nEvaluator Feedback:\n{reason}\nPlease fix the code."
                    archive_files(strategy_revision, code_revision, move_strategy=False)
                    # Continues to next code_revision
                else:
                    print("⚠️ Evaluator returned an unrecognized prefix. Treating as CODE_ERROR.")
                    code_history += f"\n\n--- PREVIOUS ATTEMPT FAILED ---\nCode:\n{generated_code}\nExecution Output:\n{execution_output}\nEvaluator Feedback:\n{evaluator_output}\nPlease fix the code based on the feedback."
                    archive_files(strategy_revision, code_revision, move_strategy=False)
    
        else:
            print(f"\n❌ Evaluator rejected the code {MAX_CODE_REVISIONS} times consecutively. Giving up completely.")
            sys.exit(1)

    else:
        print(f"\n❌ Strategy generator failed {MAX_STRATEGY_REVISIONS} times consecutively. Giving up completely.")
        sys.exit(1)

    print(f"\n✅ Done! Successful outputs saved in: {workspace}")
    print("  - strategy.txt (Idea definition)")
    print("  - script.py (Execution code)")
    print("  - *.png and *.txt (Generated results)")
    
    upload_url = "https://staging.visual-honesty.rohankapur.dev/api/developer/upload"
    honest_png = f"{file_prefix}_honest.png"
    deceptive_png = f"{file_prefix}_deceptive.png"

    if os.path.exists(honest_png) and os.path.exists(deceptive_png):
        print("🌐 Uploading generated dataset to Staging API...")
        import requests
        with open(honest_png, 'rb') as f_honest, open(deceptive_png, 'rb') as f_deceptive:
            files = {
                'honest_image': (honest_png, f_honest, 'image/png'),
                'deceptive_image': (deceptive_png, f_deceptive, 'image/png')
            }
            data = {
                'set_name': f"{file_prefix}_{timestamp}",
                'category': target_category_saved
            }
            try:
                resp = requests.post(upload_url, files=files, data=data, timeout=30)
                if resp.status_code == 200:
                    print("✅ Successfully uploaded to Staging API!")
                else:
                    print(f"⚠️ API Status Error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"⚠️ Network error uploading to API: {e}")
    else:
        print("⚠️ Skipped API upload: Rendered PNGs not found.")

if __name__ == "__main__":
    main()
