"""Minimal REST API serving content-creator CSV data as JSON.

Serves: youtube_videos.
"""

import csv
from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data" / "content-creator"


def load_csv(name):
    path = DATA_DIR / f"{name}.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {k: (None if v == "" else v) for k, v in row.items()}
            rows.append(cleaned)
    return rows


@app.route("/content-creator/youtube_videos", methods=["GET"])
def get_youtube_videos():
    return jsonify(load_csv("youtube_videos"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
