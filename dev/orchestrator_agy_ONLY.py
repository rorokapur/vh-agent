#!/usr/bin/env -S uv run

import os
import sys
import time
import re
import datetime
import subprocess
from pathlib import Path
import random

MAX_STRATEGY_REVISIONS = 10
MAX_STRATEGY_RETRIES = 3
MAX_CODE_RETRIES = 3
MAX_EVALUATOR_RETRIES = 3

PROMPTS_DIR = Path(__file__).parent / "prompts"

def load_prompt(filename, **kwargs):
    path = PROMPTS_DIR / filename
    if not path.exists():
        print(f"❌ Error: Prompt file {path} not found.")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    for k, v in kwargs.items():
        text = text.replace(f"{{{{{k.upper()}}}}}", str(v))
    return text.strip()

def _extract_strategy_field(strategy_text, field_name):
    """Extract a named field value from the plain-text strategy document."""
    pattern = rf"{field_name}:\s*(.+?)(?:\n[a-z_]+:|$)"
    match = re.search(pattern, strategy_text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _antigravity_call(prompt_text, images=None, max_retries=5):
    """Single-shot Antigravity CLI call with retry/backoff for quota limits."""
    # If images are provided, append them to prompt text using the @ syntax
    if images:
        image_lines = [f"@{os.path.abspath(img)}" for img in images]
        prompt_text = prompt_text + "\n" + "\n".join(image_lines)
        
    cmd = ["antigravity-cli", "--print", "--dangerously-skip-permissions"]
    
    backoff = 2.0
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                cmd,
                input=prompt_text.encode('utf-8'),
                capture_output=True,
                check=True
            )
            stdout_str = result.stdout.decode('utf-8').strip()
            stderr_str = result.stderr.decode('utf-8').strip()
            
            # Check if response is empty or indicates quota issue
            if not stdout_str:
                print(f"⚠️ Empty response from antigravity-cli (Attempt {attempt+1}/{max_retries}). Stderr: {stderr_str}")
                time.sleep(backoff)
                backoff *= 2
                continue
                
            if "RESOURCE_EXHAUSTED" in stderr_str or "RESOURCE_EXHAUSTED" in stdout_str or "429" in stderr_str:
                print(f"⚠️ Quota limit hit (429 / RESOURCE_EXHAUSTED). Retrying in {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
                
            return stdout_str
        except subprocess.CalledProcessError as e:
            stderr_str = e.stderr.decode('utf-8') if e.stderr else str(e)
            print(f"❌ subprocess error running antigravity-cli (Attempt {attempt+1}/{max_retries}): {stderr_str}")
            time.sleep(backoff)
            backoff *= 2
            
    raise RuntimeWarning("Failed to get response from antigravity-cli after maximum retries.")


def evaluate_gauntlet(strategy_text, image_paths, log_path="evaluator_log.txt"):
    """Sequential Evaluation Gauntlet.

    Runs the image through three checks in order:
      1. Blind Visual Extraction (parallel) — context-free interpretation of each chart.
      2. Claim Match — do the blind interpretations match the strategy goals?
      3. Side-by-Side Deception Check — does the deceptive chart actually deceive?

    Returns a dict with:
      - verdict: "PASS" or "FAIL"
      - reality_interpretation: blind extraction for the honest chart
      - narrative_interpretation: blind extraction for the deceptive chart
      - failure_reason: string describing why it failed (empty on PASS)
    """
    import concurrent.futures

    # Pull structured fields from the strategy text
    global_reality = _extract_strategy_field(strategy_text, "global_reality")
    local_narrative = _extract_strategy_field(strategy_text, "local_narrative")
    deception_technique = _extract_strategy_field(strategy_text, "deception_technique")

    # Re-identify canonical paths from filenames
    honest_path = next((p for p in image_paths if "_honest" in p), image_paths[0])
    deceptive_path = next((p for p in image_paths if "_deceptive" in p), image_paths[1])

    log_entries = []

    def append_log(label, content):
        log_entries.append(f"=== {label} ===\n{content}\n")

    def save_log():
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_entries))

    for attempt in range(MAX_EVALUATOR_RETRIES):
        log_entries.clear()

        # ── Step 1: Blind Visual Extraction (parallel) ───────────────────
        blind_prompt = load_prompt("evaluator_blind_extraction.md")
        append_log("STEP 1 PROMPT (sterile, shared)", blind_prompt)

        def _blind_call(img_path, label):
            """Run a single blind extraction call."""
            content = _antigravity_call(blind_prompt, images=[img_path])
            return label, content

        print("      > Step 1: Blind Visual Extraction (parallel)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(_blind_call, honest_path, "reality"),
                pool.submit(_blind_call, deceptive_path, "narrative"),
            ]
            results = {}
            for fut in concurrent.futures.as_completed(futures):
                label, content = fut.result()
                results[label] = content

        reality_interpretation = results["reality"]
        narrative_interpretation = results["narrative"]

        append_log("STEP 1 — REALITY INTERPRETATION (Image A / honest)", reality_interpretation)
        append_log("STEP 1 — NARRATIVE INTERPRETATION (Image B / deceptive)", narrative_interpretation)

        # ── Step 2: Claim Match Check (text-only) ────────────────────────
        prompt_2 = load_prompt(
            "evaluator_claim_match.md",
            reality_interpretation=reality_interpretation,
            narrative_interpretation=narrative_interpretation,
            global_reality=global_reality,
            local_narrative=local_narrative,
        )
        append_log("STEP 2 PROMPT", prompt_2)

        print("      > Step 2: Claim Match Check...")
        step2_content = _antigravity_call(prompt_2)
        append_log("STEP 2 RESPONSE", step2_content)

        step2_upper = step2_content.upper()

        if "[MATCH]" in step2_upper:
            # Claims aligned → proceed to deception check (Step 3)
            pass
        elif "[MISMATCH]" in step2_upper:
            # Claims didn't align → immediate FAIL, no routing needed
            save_log()
            return {
                "verdict": "FAIL",
                "reality_interpretation": reality_interpretation,
                "narrative_interpretation": narrative_interpretation,
                "failure_reason": f"Claim Match MISMATCH: The blind analyst interpretations did not align with the strategy goals. {step2_content.strip()}",
            }
        else:
            print(f"      > Step 2 formatting failed, retrying evaluation ({attempt + 1}/{MAX_EVALUATOR_RETRIES})...")
            continue

        # ── Step 3: Side-by-Side Deception Check ─────────────────────────
        prompt_3 = load_prompt(
            "evaluator_deception_check.md",
            deception_technique=deception_technique,
            global_reality=global_reality,
            local_narrative=local_narrative,
        )
        append_log("STEP 3 PROMPT", prompt_3)

        print("      > Step 3: Side-by-Side Deception Check...")
        step3_content = _antigravity_call(prompt_3, images=[honest_path, deceptive_path])
        append_log("STEP 3 RESPONSE", step3_content)

        save_log()

        step3_upper = step3_content.upper()
        if "[DECEPTION EFFECTIVE]" in step3_upper:
            return {
                "verdict": "PASS",
                "reality_interpretation": reality_interpretation,
                "narrative_interpretation": narrative_interpretation,
                "failure_reason": "",
            }
        elif "[DECEPTION FAILED" in step3_upper:
            reason_match = re.search(r"\[DECEPTION FAILED[:\s]*(.+?)\]", step3_content, re.IGNORECASE | re.DOTALL)
            reason = reason_match.group(1).strip() if reason_match else step3_content.strip()
            return {
                "verdict": "FAIL",
                "reality_interpretation": reality_interpretation,
                "narrative_interpretation": narrative_interpretation,
                "failure_reason": f"Deception Check FAILED: {reason}",
            }
        else:
            print(f"      > Step 3 formatting failed, retrying evaluation ({attempt + 1}/{MAX_EVALUATOR_RETRIES})...")
            continue

    print(f"❌ Evaluator failed to output a valid tag format after {MAX_EVALUATOR_RETRIES} retries. Giving up.")
    sys.exit(1)

def main():
    original_cwd = os.getcwd()
    
    # Default to the deception taxonomy taxonomy
    topic_path = PROMPTS_DIR / "deception_taxonomy.md"
    # If an argument is provided, treat it as extra instructions
    extra_instructions = sys.argv[1] if len(sys.argv) > 1 else ""

    categories = ["Statistics", "Encoding", "Container", "Styling"]
    formats = ["Heatmap", "Waterfall Chart", "Violin Plot", "Lollipop Chart", "Radar Chart", "Slope Graph", "Hexbin Plot", "Bubble Chart", "Treemap", "Density Plot", "Mosaic Plot", "Standard Bar Chart", "Standard Line Chart", "Scatter Plot", "Pie Chart"]

    if topic_path.exists():
        print(f"🎯 Reading prompt from file: {topic_path}")
        with open(topic_path, 'r', encoding='utf-8') as f:
            topic_text = f.read()
        
        basename = topic_path.name
        name_without_ext = topic_path.stem
        safe_topic = re.sub(r'[^a-zA-Z0-9\-_]', '', name_without_ext).lower()[:20]
    else:
        print(f"🎯 Topic specified: {topic_path}")
        topic_text = str(topic_path)
        safe_topic = re.sub(r'[^a-zA-Z0-9 \-_]', '', str(topic_path)).replace(' ', '_').lower()[:20]

    system_path = PROMPTS_DIR / "code_generator.md"
    idea_generator_path = PROMPTS_DIR / "idea_generator.md"

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

    # ═══════════════════════════════════════════════════════════════════
    # OUTER LOOP: Atomic Generation Cycles (Idea → Code → Evaluate)
    # Each iteration produces a NEW idea from the Idea Generator.
    # ═══════════════════════════════════════════════════════════════════
    for strategy_revision in range(MAX_STRATEGY_REVISIONS):
        if overall_pass:
            break

        # ── Loop 1: Generate Idea (with format retries) ──────────────
        for strategy_attempt in range(MAX_STRATEGY_RETRIES):
            print(f"\n🧠 STEP 1: Consulting Antigravity for idea generation (Revision {strategy_revision + 1}/{MAX_STRATEGY_REVISIONS}, Attempt {strategy_attempt + 1}/{MAX_STRATEGY_RETRIES})...")
            
            content = _antigravity_call(idea_history)
            
            required_keys = ["category_slug:", "context_slug:", "true_claim:", "biased_claim:"]
            missing_keys = [k for k in required_keys if k not in content]
            
            if missing_keys:
                print(f"⚠️ Strategy missing required fields: {', '.join(missing_keys)}. Retrying...")
                error_msg = load_prompt("error_strategy_format.md", missing_keys=", ".join(missing_keys))
                idea_history += f"\n\n{error_msg}"
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
            os.environ["GEMINI_WORKSPACE"] = workspace
            os.environ["ANTIGRAVITY_WORKSPACE"] = workspace
            print(f"🚀 Workspace created: {workspace}")

        if extra_instructions:
            print(f"📝 Manual instructions: {extra_instructions}")

        with open("strategy.txt", "w", encoding='utf-8') as out_f:
            out_f.write(content)

        print("📝 Strategy generated and saved to strategy.txt.")

        # ── Loop 2: Generate Code until Execution Success (Fast-Fail) ─
        code_history = ""
        run_success = False
        generated_code = ""
        execution_output = ""

        for code_attempt in range(MAX_CODE_RETRIES):
            print(f"\n🧠 STEP 2: Consulting Antigravity for Code Execution (Attempt {code_attempt + 1}/{MAX_CODE_RETRIES})...")
        
            merged_text = f"{system_text}\n{content}"
            merged_text = merged_text.replace("{{FILE_PREFIX}}", file_prefix)

            if extra_instructions:
                merged_text += f"\n\n**MANUAL INSTRUCTIONS:**\n{extra_instructions}"

            if code_history:
                code_input = f"{merged_text}\n\n{code_history}"
            else:
                code_input = merged_text

            generated_code = _antigravity_call(code_input)
            with open("script.py", "w", encoding='utf-8') as out_f:
                out_f.write(generated_code)

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
                # Fast-fail: script crashed → retry Code Generator with traceback
                print("❌ Code execution failed or images not generated.")
                error_out = execution_output if not run_success else "Images not found after execution."
                error_msg = load_prompt("error_code_execution.md", generated_code=generated_code, error_msg=error_out)
                code_history += f"\n\n{error_msg}"
                continue
            else:
                break
                
        if not run_success or not images_exist:
            print(f"\n❌ Code generator failed to produce running code {MAX_CODE_RETRIES} times. Skipping to next idea revision.")
            # Treat persistent crashes as a signal that the idea itself may be unimplementable.
            # Send global feedback to the Idea Generator and continue the outer loop.
            error_msg = load_prompt(
                "error_global_feedback.md",
                strategy=content,
                previous_code=generated_code,
                blind_reality_extraction="(code never executed successfully — no chart produced)",
                blind_narrative_extraction="(code never executed successfully — no chart produced)",
                reason=f"Code failed to execute after {MAX_CODE_RETRIES} attempts. Last error: {execution_output}",
            )
            idea_history += f"\n\n{error_msg}"
            continue

        # ── Evaluate: Sequential Validation Gauntlet ─────────────────
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

        print("👁️  Calling Evaluator Agent (Antigravity) via Sequential Gauntlet...")
        gauntlet_result = evaluate_gauntlet(content, image_paths, "evaluator_log.txt")
        print(f"⚖️  Evaluator Verdict: {gauntlet_result['verdict']}")
        if gauntlet_result['failure_reason']:
            print(f"    Reason: {gauntlet_result['failure_reason']}")

        # Archiving helper function
        def archive_files(strategy_idx):
            import shutil
            archive_dir = os.path.join(workspace, "archive", f"s{strategy_idx}")
            os.makedirs(archive_dir, exist_ok=True)
            for f in os.listdir("."):
                if os.path.isfile(f):
                    shutil.move(f, os.path.join(archive_dir, f))

        if gauntlet_result["verdict"] == "PASS":
            overall_pass = True
            break  # Exit outer loop — we're done
        else:
            # ── Global Feedback: Package entire state for Idea Generator ──
            error_msg = load_prompt(
                "error_global_feedback.md",
                strategy=content,
                previous_code=generated_code,
                blind_reality_extraction=gauntlet_result["reality_interpretation"],
                blind_narrative_extraction=gauntlet_result["narrative_interpretation"],
                reason=gauntlet_result["failure_reason"],
            )
            idea_history += f"\n\n{error_msg}"
            archive_files(strategy_revision)
            print(f"🔄 Gauntlet failed — sending global feedback to Idea Generator for a new atomic cycle.")
            # Continue outer loop with new idea

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
