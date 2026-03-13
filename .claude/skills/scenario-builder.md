---
name: scenario-builder
description: Use when creating a new eval scenario - guides through data preparation, init scripts, ground truth, and scenario config
---

# Scenario Builder Skill

Step-by-step guide for creating a new eval scenario. A scenario combines source data, init scripts, a task spec, and ground truth into a self-contained evaluation.

## When to Use

- Creating a new scenario from scratch
- Porting data from ELT-Bench or other sources
- Setting up a custom eval for a specific data domain

## Workflow

### 1. Plan the Scenario

Define:
- **Name:** short identifier (e.g., `ecommerce`, `iot-sensors`)
- **Source types:** which databases/APIs to use (Postgres, MongoDB, S3, REST API, flat files)
- **Source tables:** what data exists in each source
- **Expected output models:** what the agent should produce (with column specs)

### 2. Prepare Source Data

Create the directory structure:

```bash
mkdir -p src/data-sources/{name}/data/{name}
mkdir -p src/data-sources/{name}/gt/{name}
```

Add source CSV files to `src/data-sources/{name}/data/{name}/`:
- One CSV per source table
- Headers must match what init scripts expect
- Use consistent date formats, null handling

### 3. Write Init Scripts

Only create scripts for the source types your scenario uses.

**postgres_init.sh** (if using Postgres):
```bash
#!/bin/bash
set -e
DATA_DIR="${1:-.}/data/{name}"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -c "DROP DATABASE IF EXISTS {name};"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -c "CREATE DATABASE {name};"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -d {name} -c "
CREATE TABLE {table} ({columns});
"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -d {name} -c "\COPY {table} FROM '$DATA_DIR/{table}.csv' DELIMITER ',' CSV HEADER;"
```

**mongo_init.py** (if using MongoDB):
```python
import csv, os
from pathlib import Path
from pymongo import MongoClient
DATA_DIR = Path(__file__).parent / "data" / "{name}"
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/?directConnection=true"))
client.drop_database("{name}")
db = client["{name}"]
for table in ["{table1}", "{table2}"]:
    with open(DATA_DIR / f"{table}.csv") as f:
        rows = [row for row in csv.DictReader(f)]
    if rows:
        db[table].insert_many(rows)
```

**s3_init.sh** (if using S3/LocalStack):
```bash
#!/bin/bash
set -e
DATA_DIR="${1:-.}/data/{name}"
aws --endpoint-url=http://localhost:4566 s3 mb s3://{name}-bucket 2>/dev/null || true
aws --endpoint-url=http://localhost:4566 s3 cp "$DATA_DIR/{file}" s3://{name}-bucket/{file}
```

**api_server.py** (if using REST API):
```python
import csv
from pathlib import Path
from flask import Flask, jsonify
app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data" / "{name}"
def load_csv(name):
    with open(DATA_DIR / f"{name}.csv") as f:
        return [{k: (None if v == "" else v) for k, v in row.items()} for row in csv.DictReader(f)]
@app.route("/{name}/{endpoint}", methods=["GET"])
def get_data():
    return jsonify(load_csv("{table}"))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
```

Make shell scripts executable:
```bash
chmod +x src/data-sources/{name}/postgres_init.sh
chmod +x src/data-sources/{name}/s3_init.sh
```

### 4. Generate Ground Truth

Build the expected output yourself (SQL queries against loaded data, manual verification).

Place ground truth CSVs at `src/data-sources/{name}/gt/{name}/{model_name}.csv`:
- Headers with exact column names
- Sorted by columns 1 and 2
- Empty string for nulls
- Consistent numeric precision

### 5. Create Scenario Config

```yaml
# src/scenarios/{name}/scenario.yaml
name: {name}
description: >
  Description of what the agent must build.
spec: SPEC.md
source: {name}

credentials:
  - PG_HOST=localhost
  - PG_PORT=5433
  - PG_USER=postgres
  - PG_PASSWORD=testelt
  - PG_DATABASE={name}
  # Add all credentials the agent needs

judges:
  - correctness
  - code_quality

expected_models:
  - name: {model_name}
    ground_truth: ../../data-sources/{name}/gt/{name}/{model_name}.csv
```

### 6. Write SPEC.md

The task spec must include:
1. **Objective** — what to build (1-2 sentences)
2. **Source data** — for each source: connection details, table names, column descriptions
3. **Expected output models** — for each model: column names with descriptions
4. **Deliverable** — code in `stack/`, a `report.md`
5. **Constraints** — e.g., "everything runs locally", "no Docker"

Use `src/scenarios/github/SPEC.md` as the reference template.

### 7. Test the Scenario

```bash
# Start services
docker compose -f src/data-sources/docker-compose.yaml up -d --wait

# Load data
bash src/data-sources/{name}/postgres_init.sh src/data-sources/{name}

# Run eval
src/eval/eval.sh {name} --model claude-sonnet-4-6 --budget 5.00

# Check results
cat results/{name}/*/verdicts.json
```

## Validation Checklist

- [ ] All init scripts are idempotent (DROP + CREATE)
- [ ] Ground truth CSVs sorted by columns 1 and 2
- [ ] Credentials in scenario.yaml match init script values
- [ ] SPEC.md has exact column names for all output models
- [ ] `eval.sh` auto-detects and runs all init scripts
- [ ] At least one full eval run succeeds
