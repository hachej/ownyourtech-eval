#!/bin/bash
set -e

DB_USER="postgres"
DB_PASSWORD="testelt"
DB_NAME="content_creator"
DB_PORT="${PG_PORT:-5433}"
HOST="localhost"
DATA_DIR="${1:-.}/data/content-creator"

PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -c "CREATE DATABASE $DB_NAME;"

PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "
CREATE TABLE ghost_member (
    email TEXT,
    name TEXT,
    status TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    email_count INTEGER,
    email_opened_count INTEGER,
    email_open_rate NUMERIC
);
"
PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "\COPY ghost_member FROM '$DATA_DIR/ghost_member.csv' DELIMITER ',' CSV HEADER;"

PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "
CREATE TABLE ghost_post (
    post_id TEXT,
    title TEXT,
    slug TEXT,
    published_at TIMESTAMP WITHOUT TIME ZONE,
    word_count INTEGER,
    email_delivered_count INTEGER,
    email_opened_count INTEGER
);
"
PGPASSWORD=$DB_PASSWORD psql -h $HOST -U $DB_USER -p $DB_PORT -d $DB_NAME -c "\COPY ghost_post FROM '$DATA_DIR/ghost_post.csv' DELIMITER ',' CSV HEADER;"

echo "Content-creator postgres tables loaded."
