"""Load GitHub CSV data into MongoDB."""

import csv
import math
from pathlib import Path
from pymongo import MongoClient

DATA_DIR = Path(__file__).parent / "data" / "github"
import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/?directConnection=true")
DB_NAME = "github"

TABLES = ["issue_comment", "label", "pull_request_review", "team"]


def load():
    client = MongoClient(MONGO_URI)
    client.drop_database(DB_NAME)
    db = client[DB_NAME]

    for table in TABLES:
        csv_path = DATA_DIR / f"{table}.csv"
        if not csv_path.exists():
            print(f"SKIP {table}: {csv_path} not found")
            continue

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                cleaned = {}
                for k, v in row.items():
                    if v == "" or v is None:
                        continue
                    try:
                        fv = float(v)
                        if math.isnan(fv):
                            continue
                        cleaned[k] = int(fv) if fv == int(fv) else fv
                    except (ValueError, OverflowError):
                        cleaned[k] = v
                rows.append(cleaned)

            if rows:
                db[table].insert_many(rows)
                print(f"  {table}: {len(rows)} rows")

    print("GitHub MongoDB tables loaded.")


if __name__ == "__main__":
    load()
