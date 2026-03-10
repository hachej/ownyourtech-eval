#!/bin/bash
set -e

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-west-2
export AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"

DATA_DIR="${1:-.}/data/github"

aws --endpoint-url=$AWS_ENDPOINT_URL s3 mb s3://github-bucket 2>/dev/null || true
aws --endpoint-url=$AWS_ENDPOINT_URL s3 cp "$DATA_DIR/repo_team.jsonl" s3://github-bucket/

echo "GitHub S3 data loaded."
