#!/usr/bin/env -S uv run

import os
import sys
import re
import datetime
import subprocess
from pathlib import Path

def main():
    # Default to the deception taxonomy taxonomy
    topic_path = "prompts/deception_taxonomy.txt"
    # If an argument is provided, treat it as extra instructions
    extra_instructions = sys.argv[1] if len(sys.argv) > 1 else ""

    system_file = "prompts/system.md"

    import random
    categories = ["Statistics", "Encoding", "Container", "Styling"]

    if os.path.isfile(topic_path):
        print(f"🎯 Reading prompt from file: {topic_path}")
        with open(topic_path, 'r', encoding='utf-8') as f:
            topic_text = f.read()
        
        target_category = random.choice(categories)
        topic_text = topic_text.replace("{{TARGET_CATEGORY}}", target_category)
        print(f"🎲 Randomly assigned deception category: {target_category}")
        
        basename = os.path.basename(topic_path)
        name_without_ext = os.path.splitext(basename)[0]
        # Equivalent to: tr -dc '[:alnum:]\-_' | tr '[:upper:]' '[:lower:]' | cut -c 1-20
        safe_topic = re.sub(r'[^a-zA-Z0-9\-_]', '', name_without_ext).lower()[:20]
    else:
        print(f"🎯 Topic specified: {topic_path}")
        topic_text = topic_path
        # Equivalent to: tr -dc '[:alnum:] \-_' | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | cut -c 1-20
        safe_topic = re.sub(r'[^a-zA-Z0-9 \-_]', '', topic_path)
        safe_topic = safe_topic.replace(' ', '_').lower()[:20]

    # 1. Verify system file exists
    if not os.path.isfile(system_file):
        print(f"❌ Error: System prompt {system_file} not found.")
        sys.exit(1)

    system_path = Path(system_file).resolve()
    idea_generator_path = Path("prompts/idea_generator.md").resolve()
    ollama_model = "gemma4:26b"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    date_str = datetime.datetime.now().strftime("%Y%m%d")

    print(f"🧠 STEP 1: Consulting Ollama ({ollama_model}) for idea generation...")
    import ollama
    with open(idea_generator_path, 'r', encoding='utf-8') as f:
        idea_prompt = f.read()
    
    ollama_input = f"{idea_prompt}\n\n**PROMPT/TOPIC:**\n{topic_text}"
    client = ollama.Client(host='http://127.0.0.1:11434')
    response = client.chat(
        model=ollama_model,
        messages=[{'role': 'user', 'content': ollama_input}]
    )
    
    content = getattr(response.message, 'content', '') if hasattr(response, 'message') else response.get('message', {}).get('content', '')
    content = content.strip()

    category_slug = "unknown"
    context_slug = "unknown"
    cat_match = re.search(r"category_slug:\s*([a-zA-Z0-9_\-]+)", content)
    if cat_match: category_slug = cat_match.group(1).lower()
    ctx_match = re.search(r"context_slug:\s*([a-zA-Z0-9_\-]+)", content)
    if ctx_match: context_slug = ctx_match.group(1).lower()

    file_prefix = f"{category_slug}_{context_slug}_{date_str}"

    # 2. Create and enter the workspace
    workspace = f"output/{file_prefix}_{timestamp}"
    os.makedirs(workspace, exist_ok=True)

    # Change directory (affects the current process and its subprocesses)
    os.chdir(workspace)
    print(f"🚀 Workspace created: {workspace}")

    if extra_instructions:
        print(f"📝 Manual instructions: {extra_instructions}")

    with open("strategy.txt", "w", encoding='utf-8') as out_f:
        out_f.write(content)

    print("📝 Strategy generated and saved to strategy.txt.")

    print("🧠 STEP 2: Consulting Gemini for Code Execution...")
    with open(system_path, 'r', encoding='utf-8') as f:
        system_text = f.read()
    
    with open("strategy.txt", 'r', encoding='utf-8') as f:
        strategy_text = f.read()

    merged_text = f"{system_text}\n{strategy_text}"
    merged_text = merged_text.replace("{{FILE_PREFIX}}", file_prefix)

    if extra_instructions:
        merged_text += f"\n\n**MANUAL INSTRUCTIONS:**\n{extra_instructions}"

    with open("script.py", "w", encoding='utf-8') as out_f:
        subprocess.run(
            ["gemini", "-m", "gemini-3-flash-preview"],
            input=merged_text.encode('utf-8'),
            stdout=out_f,
            check=True
        )

    print("📊 Rendering charts...")
    subprocess.run(["uv", "run", "script.py"], check=True)

    print(f"✅ Done! Outputs saved in: {workspace}")
    print("  - strategy.txt (Idea definition)")
    print("  - script.py (Execution code)")
    print("  - *.png and *.txt (Generated results)")

if __name__ == "__main__":
    main()
