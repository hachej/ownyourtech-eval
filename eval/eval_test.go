package eval

import (
	"os"
	"path/filepath"
	"testing"
)

func kgRoot(t *testing.T) string {
	t.Helper()
	// Walk up from test file to repo root
	wd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	root := filepath.Join(filepath.Dir(wd), "kg")
	if _, err := os.Stat(root); err != nil {
		t.Skipf("kg/ not found at %s", root)
	}
	return root
}

func TestEvaluate_Approved(t *testing.T) {
	kb := New(kgRoot(t))

	cases := []struct {
		proposal string
		wantItem string
	}{
		{"Use dlt for ingestion", "dlt"},
		{"Store data in DuckDB", "DuckDB"},
		{"Deploy on Hetzner Cloud", "Hetzner Cloud"},
		{"Transform with dbt-core", "dbt-core"},
		{"Schedule with Cron", "Cron"},
	}

	for _, tc := range cases {
		t.Run(tc.proposal, func(t *testing.T) {
			r, err := kb.Evaluate(tc.proposal)
			if err != nil {
				t.Fatal(err)
			}
			if !r.Approved {
				t.Errorf("expected approved, got rejected: %s", r.Recommendation)
			}
			if r.Tier != 0 {
				t.Errorf("expected tier 0, got tier %d", r.Tier)
			}
			found := false
			for _, m := range r.MatchedItems {
				if m.Solution == tc.wantItem {
					found = true
				}
			}
			if !found {
				t.Errorf("expected matched item %q, got %v", tc.wantItem, r.MatchedItems)
			}
		})
	}
}

func TestEvaluate_Rejected(t *testing.T) {
	kb := New(kgRoot(t))

	cases := []struct {
		proposal     string
		wantConflict string
	}{
		{"Use Snowflake for the warehouse", "Snowflake"},
		{"Deploy to AWS", "AWS"},
		{"Ingest with Fivetran", "Fivetran"},
		{"Use BigQuery for analytics", "BigQuery"},
		{"Set up dbt Cloud", "dbt Cloud"},
		{"Track events with Segment", "Segment"},
	}

	for _, tc := range cases {
		t.Run(tc.proposal, func(t *testing.T) {
			r, err := kb.Evaluate(tc.proposal)
			if err != nil {
				t.Fatal(err)
			}
			if r.Approved {
				t.Error("expected rejected, got approved")
			}
			if r.Tier != 1 {
				t.Errorf("expected tier 1, got tier %d", r.Tier)
			}
			found := false
			for _, c := range r.Conflicts {
				if c.Tier == 1 {
					found = true
				}
			}
			if !found {
				t.Error("expected tier 1 conflict")
			}
		})
	}
}

func TestEvaluate_Warning(t *testing.T) {
	kb := New(kgRoot(t))

	cases := []struct {
		proposal string
	}{
		{"Use CSV for data exchange"},
		{"Set up Airflow for orchestration"},
	}

	for _, tc := range cases {
		t.Run(tc.proposal, func(t *testing.T) {
			r, err := kb.Evaluate(tc.proposal)
			if err != nil {
				t.Fatal(err)
			}
			if !r.Approved {
				t.Error("expected approved (with warning), got rejected")
			}
			if r.Tier != 2 {
				t.Errorf("expected tier 2, got tier %d", r.Tier)
			}
		})
	}
}

func TestEvaluate_NoMatch(t *testing.T) {
	kb := New(kgRoot(t))

	r, err := kb.Evaluate("use some totally unknown tool xyz123")
	if err != nil {
		t.Fatal(err)
	}
	if !r.Approved {
		t.Error("expected approved (no match means manual check)")
	}
	if len(r.MatchedItems) != 0 {
		t.Errorf("expected no matches, got %d", len(r.MatchedItems))
	}
}

func TestEvaluate_AlternativesSuggested(t *testing.T) {
	kb := New(kgRoot(t))

	r, err := kb.Evaluate("Use Snowflake for analytics")
	if err != nil {
		t.Fatal(err)
	}
	if r.Approved {
		t.Error("expected rejected")
	}

	hasAlts := false
	for _, c := range r.Conflicts {
		if len(c.Alternatives) > 0 {
			hasAlts = true
		}
	}
	if !hasAlts {
		t.Error("expected alternatives to be suggested for rejected tool")
	}
}

func TestList(t *testing.T) {
	kb := New(kgRoot(t))
	entries, err := kb.List()
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) == 0 {
		t.Error("expected entries in KB")
	}

	categories := map[string]bool{}
	for _, e := range entries {
		categories[e.Category] = true
	}
	for _, want := range []string{"principles", "catalog", "patterns", "anti-patterns"} {
		if !categories[want] {
			t.Errorf("missing category: %s", want)
		}
	}
}
