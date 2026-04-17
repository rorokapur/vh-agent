#!/bin/zsh

# Usage: ./generate.sh ["Extra Instructions"]

# Default to the deception taxonomy taxonomy
TOPIC="prompts/deception_taxonomy.txt"
# If an argument is provided, treat it as extra instructions
EXTRA_INSTRUCTIONS=$1

SYSTEM_FILE="prompts/system.md"

if [[ -f "$TOPIC" ]]; then
    echo "🎯 Reading prompt from file: $TOPIC"
    TOPIC_TEXT=$(cat "$TOPIC")
    # Use the filename without extension for the safe topic
    BASENAME=$(basename "$TOPIC")
    SAFE_TOPIC=$(echo "${BASENAME%.*}" | tr -dc '[:alnum:]\-_' | tr '[:upper:]' '[:lower:]' | cut -c 1-20)
else
    echo "🎯 Topic specified: $TOPIC"
    TOPIC_TEXT="$TOPIC"
    # Sanitize topic for filename usage (replace spaces with underscores, alphanumeric only)
    SAFE_TOPIC=$(echo "$TOPIC" | tr -dc '[:alnum:] \-_' | tr ' ' '_' | tr '[:upper:]' '[:lower:]' | cut -c 1-20)
fi

# 1. Verify system file exists
if [[ ! -f "$SYSTEM_FILE" ]]; then
    echo "❌ Error: System prompt $SYSTEM_FILE not found."
    exit 1
fi

# 2. Create and enter the workspace
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORKSPACE="output/${SAFE_TOPIC}_${TIMESTAMP}"
mkdir -p "$WORKSPACE"

# Capture absolute paths before cd
SYSTEM_PATH=$(realpath "$SYSTEM_FILE")
IDEA_GENERATOR_PATH=$(realpath "prompts/idea_generator.md")
OLLAMA_MODEL="gemma4:26b"

cd "$WORKSPACE" || exit

echo "🚀 Workspace created: $WORKSPACE"
if [[ -n "$EXTRA_INSTRUCTIONS" ]]; then
    echo "📝 Manual instructions: $EXTRA_INSTRUCTIONS"
fi

echo "🧠 STEP 1: Consulting Ollama ($OLLAMA_MODEL) for idea generation..."
# We pass the prompt and append the topic text at the end for Ollama to ingest
{ cat "$IDEA_GENERATOR_PATH"; echo -e "\n\n**PROMPT/TOPIC:**\n$TOPIC_TEXT"; } | ollama run "$OLLAMA_MODEL" > strategy.txt
echo "📝 Strategy generated and saved to strategy.txt."

echo "🧠 STEP 2: Consulting Gemini for Code Execution..."
# 4. Concatenate and Pipe
# Using '|' as a delimiter for sed to avoid path slash conflicts
{ cat "$SYSTEM_PATH" "strategy.txt" | sed "s|{{TOPIC}}|${SAFE_TOPIC}|g"; echo -e "${EXTRA_INSTRUCTIONS:+\n\n**MANUAL INSTRUCTIONS:**\n$EXTRA_INSTRUCTIONS}"; } | gemini -m gemini-3.1-pro-preview > script.py

# 5. Execute via uv
echo "📊 Rendering charts..."
uv run script.py

echo "✅ Done! Outputs saved in: $WORKSPACE"
echo "  - strategy.txt (Idea definition)"
echo "  - script.py (Execution code)"
echo "  - *.png and *.txt (Generated results)"

# Return to root
cd - > /dev/null