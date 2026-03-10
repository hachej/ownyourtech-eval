#!/bin/bash
set -euo pipefail

# Usage: ./eval.sh <scenario-name> [--model <model>] [--budget <usd>]
# Example: ./eval.sh github --model claude-sonnet-4-6 --budget 5.00

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(cd "$EVAL_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SRC_DIR/.." && pwd)"

SCENARIO_NAME="${1:?Usage: eval.sh <scenario-name>}"
SCENARIO_DIR="$SRC_DIR/scenarios/$SCENARIO_NAME"
MODEL="${MODEL:-claude-sonnet-4-6}"
BUDGET="${BUDGET:-5.00}"

# Parse optional flags
shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --budget) BUDGET="$2"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

SCENARIO="$SCENARIO_DIR/scenario.yaml"
if [ ! -f "$SCENARIO" ]; then
  echo "FAIL: $SCENARIO not found" >&2
  exit 1
fi

# Create isolated workdir for agent
WORKDIR=$(mktemp -d "/tmp/eval-${SCENARIO_NAME}-XXXXXX")
RUN_ID="$(date +%Y%m%d-%H%M%S)-${MODEL##*-}"
RESULTS_DIR="$REPO_ROOT/results/$SCENARIO_NAME/$RUN_ID"
mkdir -p "$RESULTS_DIR"

echo "=== Eval: $SCENARIO_NAME ==="
echo "Model:   $MODEL"
echo "Budget:  \$$BUDGET"
echo "Workdir: $WORKDIR"
echo "Results: $RESULTS_DIR"
echo ""

# --- Step 1: Setup sources ---
echo "--- Setting up sources ---"
cd "$EVAL_DIR"
docker compose -f "$SRC_DIR/data-sources/docker-compose.yaml" up -d --wait 2>&1 | tail -5

SOURCES_DIR="$SRC_DIR/data-sources"

# Load data into Postgres
if [ -f "$SOURCES_DIR/$SCENARIO_NAME/postgres_init.sh" ]; then
  echo "Loading Postgres data..."
  bash "$SOURCES_DIR/$SCENARIO_NAME/postgres_init.sh" "$SOURCES_DIR/$SCENARIO_NAME"
fi

# Load data into MongoDB
if [ -f "$SOURCES_DIR/$SCENARIO_NAME/mongo_init.py" ]; then
  echo "Loading MongoDB data..."
  python3 "$SOURCES_DIR/$SCENARIO_NAME/mongo_init.py"
fi

# Load data into S3
if [ -f "$SOURCES_DIR/$SCENARIO_NAME/s3_init.sh" ]; then
  echo "Loading S3 data..."
  bash "$SOURCES_DIR/$SCENARIO_NAME/s3_init.sh" "$SOURCES_DIR/$SCENARIO_NAME"
fi

# Copy flat files into workdir
echo "Copying flat files..."
if [ -d "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME" ]; then
  mkdir -p "$WORKDIR/data/$SCENARIO_NAME"
  # Copy only flat files referenced in source.yaml (csv, jsonl)
  for f in "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME"/*.csv "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME"/*.jsonl; do
    [ -f "$f" ] && cp "$f" "$WORKDIR/data/$SCENARIO_NAME/"
  done
fi

echo "Sources ready."
echo ""

# --- Step 2: Prepare workdir ---
git init -q "$WORKDIR"
cp "$SCENARIO_DIR/SPEC.md" "$WORKDIR/SPEC.md"
cp "$EVAL_DIR/CLAUDE.md" "$WORKDIR/CLAUDE.md"

# Export credentials as env vars
echo "--- Credentials ---"
while IFS= read -r line; do
  line=$(echo "$line" | sed 's/^- //')
  export "$line"
  echo "  $line"
done < <(yq -r '.credentials[]' "$SCENARIO")
echo ""

# --- Step 3: Ensure oyt CLI is available ---
echo "--- Checking oyt CLI ---"
if ! command -v oyt &>/dev/null; then
  echo "WARN: oyt CLI not found in PATH."
  echo "Install it: pip install oyt  (or build from https://github.com/hachej/ownyourtech-cli)"
  echo "The agent will not be able to consult the knowledge base."
fi

# --- Step 4: Run agent ---
echo "--- Running agent ---"
cd "$WORKDIR"

START_TIME=$(date +%s)

AGENT_INSTRUCTIONS=$(cat "$EVAL_DIR/CLAUDE.md")

env -u CLAUDECODE OYT_KB_PATH="${OYT_KB_PATH:-}" claude \
  -p \
  --dangerously-skip-permissions \
  --model "$MODEL" \
  --max-turns 100 \
  --max-budget-usd "$BUDGET" \
  --output-format stream-json \
  --verbose \
  --append-system-prompt "$AGENT_INSTRUCTIONS" \
  "Read SPEC.md and build the complete solution. Run it to verify it works." \
  > "$RESULTS_DIR/agent.jsonl" \
  2> "$RESULTS_DIR/agent.stderr.log" \
  || true

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Extract readable log from JSONL
python3 -c "
import json, sys
for line in open('$RESULTS_DIR/agent.jsonl'):
    line = line.strip()
    if not line: continue
    try:
        msg = json.loads(line)
        t = msg.get('type', '')
        if t == 'assistant':
            for block in msg.get('content', []):
                bt = block.get('type', '')
                if bt == 'text':
                    print(block['text'])
                elif bt == 'tool_use':
                    print(f'[TOOL: {block[\"name\"]}] {json.dumps(block.get(\"input\", {}))[:300]}')
        elif t == 'tool_result':
            content = msg.get('content', '')
            if isinstance(content, list):
                content = ' '.join(b.get('text', '') for b in content if isinstance(b, dict))
            print(f'[RESULT] {str(content)[:300]}')
        elif t == 'result':
            for block in msg.get('content', []) if isinstance(msg.get('content'), list) else []:
                if block.get('type') == 'text':
                    print(block['text'])
    except (json.JSONDecodeError, KeyError):
        pass
" > "$RESULTS_DIR/agent.log" 2>/dev/null || true

echo "Agent finished in ${DURATION}s"
echo "Agent log: $RESULTS_DIR/agent.log"
echo ""

# --- Step 5: Run judges ---
echo "--- Running judges ---"
python3 "$SRC_DIR/judges/base.py" \
  "$SCENARIO_DIR" "$WORKDIR" "$RESULTS_DIR" "$MODEL" \
  | tee "$RESULTS_DIR/judges.log" || true

# --- Step 6: Write metadata ---
cat > "$RESULTS_DIR/meta.yaml" <<EOF
scenario: $SCENARIO_NAME
model: $MODEL
budget: $BUDGET
run_id: $RUN_ID
duration_seconds: $DURATION
workdir: $WORKDIR
timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

echo ""
echo "Done. Results in $RESULTS_DIR"
