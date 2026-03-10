"""Minimal REST API serving GitHub CSV data as JSON.

Replicates ELT-Bench's Flask API for the github dataset.
Serves: issue_assignee, issue_merged, repository.
"""

import csv
from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data" / "github"


def load_csv(name):
    path = DATA_DIR / f"{name}.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {k: (None if v == "" else v) for k, v in row.items()}
            rows.append(cleaned)
    return rows


@app.route("/github/issue_assignee", methods=["GET"])
def get_issue_assignee():
    return jsonify(load_csv("issue_assignee"))


@app.route("/github/issue_merged", methods=["GET"])
def get_issue_merged():
    return jsonify(load_csv("issue_merged"))


@app.route("/github/repository", methods=["GET"])
def get_repository():
    return jsonify(load_csv("repository"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
