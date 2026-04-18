#!/usr/bin/env -S uv run

import os
import sys
import re
import datetime
import subprocess
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
# Set this to the exact name of the model installed in your local Ollama instance
OLLAMA_MODEL = "gemma4:26b"
# ==========================================

def main():
    topic_path = "prompts/deception_taxonomy.md"
    extra_instructions = sys.argv[1] if len(sys.argv) > 1 else ""
    system_file = "prompts/system.md"

    import random
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
        safe_topic = re.sub(r'[^a-zA-Z0-9 \-_]', '', topic_path)
        safe_topic = safe_topic.replace(' ', '_').lower()[:20]

    if not os.path.isfile(system_file):
        print(f"❌ Error: System prompt {system_file} not found.")
        sys.exit(1)

    system_path = Path(system_file).resolve()
    idea_generator_path = Path("prompts/idea_generator.md").resolve()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    print(f"🧠 STEP 1: Consulting Ollama ({OLLAMA_MODEL}) for idea generation...")
    import ollama
    
    with open(idea_generator_path, 'r', encoding='utf-8') as f:
        idea_prompt = f.read()
    
    target_category = random.choice(categories)
    target_format = random.choice(formats)
    print(f"🎲 Randomly assigned deception category: {target_category}")
    print(f"🎲 Randomly assigned chart format: {target_format}")
    
    idea_prompt = idea_prompt.replace("{{TARGET_CATEGORY}}", target_category)
    idea_prompt = idea_prompt.replace("{{TARGET_FORMAT}}", target_format)
    
    client = ollama.Client(host='http://127.0.0.1:11434')
    ollama_input = f"{idea_prompt}\n\n**PROMPT/TOPIC:**\n{topic_text}"
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{'role': 'user', 'content': ollama_input}]
    )
    
    content = getattr(response.message, 'content', '') if hasattr(response, 'message') else response.get('message', {}).get('content', '')
    content = content.strip()
    
    # Natively strip any "chain of thought" or conversational preamble LLMs output
    if "category_slug:" in content:
        content = "category_slug:" + content.split("category_slug:", 1)[1]

    category_slug = "unknown"
    context_slug = "unknown"
    cat_match = re.search(r"category_slug:\s*([a-zA-Z0-9_\-]+)", content)
    if cat_match: category_slug = cat_match.group(1).lower()
    ctx_match = re.search(r"context_slug:\s*([a-zA-Z0-9_\-]+)", content)
    if ctx_match: context_slug = ctx_match.group(1).lower()

    file_prefix = f"{category_slug}_{context_slug}_{date_str}"

    workspace = f"output/{file_prefix}_{timestamp}"
    os.makedirs(workspace, exist_ok=True)
    os.chdir(workspace)
    print(f"🚀 Workspace created: {workspace}")

    if extra_instructions:
        print(f"📝 Manual instructions: {extra_instructions}")

    with open("strategy.txt", "w", encoding='utf-8') as out_f:
        out_f.write(content)

    print("📝 Strategy generated and saved to strategy.txt.")

    print(f"🧠 STEP 2: Consulting Ollama ({OLLAMA_MODEL}) for Code Execution...")
    with open(system_path, 'r', encoding='utf-8') as f:
        system_text = f.read()
    
    with open("strategy.txt", 'r', encoding='utf-8') as f:
        strategy_text = f.read()

    merged_text = f"{system_text}\n{strategy_text}"
    merged_text = merged_text.replace("{{FILE_PREFIX}}", file_prefix)

    if extra_instructions:
        merged_text += f"\n\n**MANUAL INSTRUCTIONS:**\n{extra_instructions}"

    code_response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{'role': 'user', 'content': merged_text}]
    )
    
    code_content = getattr(code_response.message, 'content', '') if hasattr(code_response, 'message') else code_response.get('message', {}).get('content', '')
    code_content = code_content.strip()
    
    # Strip markdown wrappers naturally produced by local models
    if "```python" in code_content:
        code_content = code_content.split("```python")[1].split("```")[0]
    elif "```" in code_content:
        code_content = code_content.split("```")[1].split("```")[0]

    # Smaller/experimental Gemma models often leak raw vocabulary tokens like <unused56>
    # This regex aggressively scrubs those tokens out so they don't break Python syntax
    code_content = re.sub(r'<unused\d+>', '', code_content)
    code_content = code_content.replace('<eos>', '').replace('<bos>', '')

    with open("script.py", "w", encoding='utf-8') as out_f:
        out_f.write(code_content.strip() + "\n")

    print("📊 Rendering charts...")
    max_retries = 3
    for attempt in range(max_retries):
        run_result = subprocess.run(["uv", "run", "script.py"], capture_output=True, text=True)
        if run_result.returncode == 0:
            break
        
        match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", run_result.stderr)
        if match:
            missing_module = match.group(1)
            print(f"📦 Auto-installing missing module '{missing_module}'...")
            subprocess.run(["uv", "pip", "install", missing_module], check=True)
            print("🔄 Retrying script execution...")
        else:
            print(f"⚠️ Script execution failed:\n{run_result.stderr}")
            sys.exit(1)

    print(f"✅ Done! Outputs saved in: {workspace}")
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
                'category': target_category
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
