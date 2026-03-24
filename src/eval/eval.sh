#!/bin/bash
set -euo pipefail

# Usage: ./eval.sh <scenario-name> [--model <model>] [--budget <usd>]
# Example: ./eval.sh content-creator --model claude-sonnet-4-6 --budget 10.00

EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$(cd "$EVAL_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SRC_DIR/.." && pwd)"

SCENARIO_NAME="${1:?Usage: eval.sh <scenario-name>}"
SCENARIO_DIR="$SRC_DIR/scenarios/$SCENARIO_NAME"
MODEL="${MODEL:-claude-sonnet-4-6}"
BUDGET="${BUDGET:-10.00}"

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

# --- Step 1: Load credentials ---
# Source .env file if present (API-based scenarios)
if [ -f "$SCENARIO_DIR/.env" ]; then
  echo "--- Loading .env credentials ---"
  set -a
  source "$SCENARIO_DIR/.env"
  set +a
fi

# Export credentials from scenario.yaml
echo "--- Credentials ---"
while IFS= read -r line; do
  line=$(echo "$line" | sed 's/^- //')
  # Expand env var references like ${GHOST_API_URL}
  expanded=$(eval echo "$line")
  export "$expanded"
  # Mask secrets in output
  key="${expanded%%=*}"
  val="${expanded#*=}"
  if [ ${#val} -gt 8 ]; then
    echo "  ${key}=${val:0:4}...${val: -4}"
  else
    echo "  ${key}=${val}"
  fi
done < <(yq -r '.credentials[]' "$SCENARIO")
echo ""

# --- Step 2: Setup sources (Docker-based scenarios only) ---
SOURCES_DIR="$SRC_DIR/data-sources"
HAS_DOCKER_SOURCES=false

if [ -f "$SOURCES_DIR/$SCENARIO_NAME/postgres_init.sh" ] || \
   [ -f "$SOURCES_DIR/$SCENARIO_NAME/mongo_init.py" ] || \
   [ -f "$SOURCES_DIR/$SCENARIO_NAME/s3_init.sh" ]; then
  HAS_DOCKER_SOURCES=true
fi

if [ "$HAS_DOCKER_SOURCES" = true ]; then
  echo "--- Setting up Docker sources ---"
  docker compose -f "$SOURCES_DIR/docker-compose.yaml" up -d --wait 2>&1 | tail -5

  if [ -f "$SOURCES_DIR/$SCENARIO_NAME/postgres_init.sh" ]; then
    echo "Loading Postgres data..."
    bash "$SOURCES_DIR/$SCENARIO_NAME/postgres_init.sh" "$SOURCES_DIR/$SCENARIO_NAME"
  fi

  if [ -f "$SOURCES_DIR/$SCENARIO_NAME/mongo_init.py" ]; then
    echo "Loading MongoDB data..."
    python3 "$SOURCES_DIR/$SCENARIO_NAME/mongo_init.py"
  fi

  if [ -f "$SOURCES_DIR/$SCENARIO_NAME/s3_init.sh" ]; then
    echo "Loading S3 data..."
    bash "$SOURCES_DIR/$SCENARIO_NAME/s3_init.sh" "$SOURCES_DIR/$SCENARIO_NAME"
  fi

  echo "Docker sources ready."
  echo ""
fi

# Copy flat files into workdir (if any)
if [ -d "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME" ]; then
  echo "Copying flat files..."
  mkdir -p "$WORKDIR/data/$SCENARIO_NAME"
  for f in "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME"/*.csv "$SOURCES_DIR/$SCENARIO_NAME/data/$SCENARIO_NAME"/*.jsonl; do
    [ -f "$f" ] && cp "$f" "$WORKDIR/data/$SCENARIO_NAME/"
  done
fi

# --- Step 3: Prepare workdir ---
git init -q "$WORKDIR"
cp "$SCENARIO_DIR/SPEC.md" "$WORKDIR/SPEC.md"
cp "$EVAL_DIR/CLAUDE.md" "$WORKDIR/CLAUDE.md"

# Copy persona file if present
if [ -f "$SCENARIO_DIR/persona.yaml" ]; then
  cp "$SCENARIO_DIR/persona.yaml" "$WORKDIR/persona.yaml"
fi

# Write .env to workdir so agent can use python-dotenv etc.
if [ -f "$SCENARIO_DIR/.env" ]; then
  cp "$SCENARIO_DIR/.env" "$WORKDIR/.env"
fi

# --- Step 4: Ensure oyt CLI is available ---
echo "--- Checking oyt CLI ---"
if ! command -v oyt &>/dev/null; then
  echo "WARN: oyt CLI not found in PATH."
  echo "Install it: pip install oyt  (or build from https://github.com/hachej/ownyourtech-cli)"
  echo "The agent will not be able to consult the knowledge base."
fi

# --- Step 5: Run agent ---
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
  "Read SPEC.md to understand the task. If persona.yaml exists, read it first to understand who you are helping and what platforms they use. Then build the complete solution. Run it to verify it works." \
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

# --- Step 6: Run judges ---
echo "--- Running judges ---"
python3 "$SRC_DIR/judges/base.py" \
  "$SCENARIO_DIR" "$WORKDIR" "$RESULTS_DIR" "$MODEL" \
  | tee "$RESULTS_DIR/judges.log" || true

# --- Step 7: Capture git diff ---
SEED_COMMIT=$(cd "$WORKDIR" && git rev-list --max-parents=0 HEAD 2>/dev/null || echo "")
if [ -n "$SEED_COMMIT" ]; then
  (cd "$WORKDIR" && git diff "${SEED_COMMIT}"..HEAD --stat > "$RESULTS_DIR/diff-stat.txt" 2>/dev/null || true)
  (cd "$WORKDIR" && git diff "${SEED_COMMIT}"..HEAD > "$RESULTS_DIR/diff.txt" 2>/dev/null || true)
fi

# --- Step 8: Write metadata ---
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
