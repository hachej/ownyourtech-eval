.PHONY: test build run-examples clean

test:
	go test ./eval/ -v

build:
	go build -o oyt-eval ./cmd/oyt-eval/

run-examples: build
	@echo "=== Approved (Strong Defaults) ==="
	@./oyt-eval "Use dlt for ingestion" || true
	@echo ""
	@./oyt-eval "Store in DuckDB" || true
	@echo ""
	@./oyt-eval "Deploy on Hetzner Cloud" || true
	@echo ""
	@echo "=== Rejected (Tier 1 Violations) ==="
	@./oyt-eval "Use Snowflake for analytics" || true
	@echo ""
	@./oyt-eval "Deploy to AWS" || true
	@echo ""
	@./oyt-eval "Ingest with Fivetran" || true
	@echo ""
	@echo "=== Warning (Tier 2 Deviations) ==="
	@./oyt-eval "Use CSV for data exchange" || true
	@echo ""
	@./oyt-eval "Set up Airflow" || true

clean:
	rm -f oyt-eval
