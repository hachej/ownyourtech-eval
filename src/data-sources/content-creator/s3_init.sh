#!/bin/bash
set -e

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-west-2
export AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"

DATA_DIR="${1:-.}/data/content-creator"

aws --endpoint-url=$AWS_ENDPOINT_URL s3 mb s3://content-creator-bucket 2>/dev/null || true
aws --endpoint-url=$AWS_ENDPOINT_URL s3 cp "$DATA_DIR/shortio_clicks.jsonl" s3://content-creator-bucket/
aws --endpoint-url=$AWS_ENDPOINT_URL s3 cp "$DATA_DIR/walker_events.jsonl" s3://content-creator-bucket/

echo "Content-creator S3 data loaded."
