#!/bin/zsh

# Usage: ./generate.sh data_cropping
TECHNIQUE=$1
EXTRA_INSTRUCTIONS=$2
SYSTEM_FILE="prompts/system.md"
PROMPTS_ROOT="prompts"

# 1. Verify system file exists
if [[ ! -f "$SYSTEM_FILE" ]]; then
    echo "❌ Error: System prompt $SYSTEM_FILE not found."
    exit 1
fi

# 2. Find the technique file anywhere inside the prompts folder
# This searches recursively through all subfolders
TECHNIQUE_FILE=$(find "$PROMPTS_ROOT" -name "${TECHNIQUE}.md" -print -quit)

if [[ -z "$TECHNIQUE_FILE" ]]; then
    echo "❌ Error: Technique file '${TECHNIQUE}.md' not found anywhere inside $PROMPTS_ROOT."
    exit 1
fi

# 3. Create and enter the workspace
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORKSPACE="output/${TECHNIQUE}_${TIMESTAMP}"
mkdir -p "$WORKSPACE"

# Capture absolute paths before cd
SYSTEM_PATH=$(realpath "$SYSTEM_FILE")
TECHNIQUE_PATH=$(realpath "$TECHNIQUE_FILE")

cd "$WORKSPACE" || exit

echo "🚀 Workspace created: $WORKSPACE"
echo "📂 Found technique at: $TECHNIQUE_PATH"
if [[ -n "$EXTRA_INSTRUCTIONS" ]]; then
    echo "📝 Manual instructions: $EXTRA_INSTRUCTIONS"
fi
echo "🧠 Consulting Gemini for $TECHNIQUE..."

# 4. Concatenate and Pipe
# Using '|' as a delimiter for sed to avoid path slash conflicts
{ cat "$SYSTEM_PATH" "$TECHNIQUE_PATH" | sed "s|{{TECHNIQUE}}|${TECHNIQUE}|g"; echo -e "${EXTRA_INSTRUCTIONS:+\n\n**MANUAL INSTRUCTIONS:**\n$EXTRA_INSTRUCTIONS}"; } | gemini -m gemini-3.1-pro-preview > script.py

# 5. Execute via uv
echo "📊 Rendering charts..."
uv run script.py

echo "✅ Done! Check the output in $WORKSPACE"

# Return to root
cd - > /dev/null