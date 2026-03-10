// Package eval evaluates technology proposals against the OwnYourTech knowledge base.
//
// The knowledge base encodes opinionated recommendations for EU-sovereign,
// open-source, local-first data stacks. Proposals are matched against a
// catalog of solutions and checked for tier violations:
//
//   - Tier 1 (Reject): Non-negotiable violations (EU sovereignty, open source, local-first)
//   - Tier 2 (Avoid):  Deviations from strong defaults (warnings, not blocking)
//   - Tier 0 (OK):     Aligns with recommendations
package eval

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Result represents the outcome of evaluating a proposal against the KB.
type Result struct {
	Approved       bool          `json:"approved"`
	Tier           int           `json:"tier"`
	Conflicts      []Conflict    `json:"conflicts"`
	Recommendation string        `json:"recommendation"`
	MatchedItems   []MatchedItem `json:"matched_items"`
}

// Conflict describes a specific violation found during evaluation.
type Conflict struct {
	Tier         int      `json:"tier"`
	Source       string   `json:"source"`
	Message      string   `json:"message"`
	Alternatives []string `json:"alternatives,omitempty"`
}

// MatchedItem is a catalog entry that matched the proposal.
type MatchedItem struct {
	Solution       string `json:"solution"`
	Recommendation string `json:"recommendation"`
	Qualifier      string `json:"qualifier"`
	Category       string `json:"category"`
	Context        string `json:"context"`
}

// Entry represents a single KB document.
type Entry struct {
	Path     string // relative path within KB (e.g. "catalog/ingestion")
	Category string // top-level category
	Name     string // filename without extension
	Content  string
}

type catalogItem struct {
	category       string
	solution       string
	recommendation string
	qualifier      string
	context        string
}

// KB provides access to the knowledge base files.
type KB struct {
	Root string
}

// New creates a KB rooted at the given directory.
func New(root string) *KB {
	return &KB{Root: root}
}

// Resolve finds the KB root directory. Checks:
// 1. OYT_KB_PATH env var
// 2. ./kg/ relative to cwd
// 3. Walk up to find kg/ in parent directories
func Resolve() (string, error) {
	if p := os.Getenv("OYT_KB_PATH"); p != "" {
		if info, err := os.Stat(p); err == nil && info.IsDir() {
			return p, nil
		}
		return "", fmt.Errorf("OYT_KB_PATH=%s does not exist", p)
	}

	cwd, err := os.Getwd()
	if err != nil {
		return "", err
	}

	dir := cwd
	for {
		candidate := filepath.Join(dir, "kg")
		if info, err := os.Stat(candidate); err == nil && info.IsDir() {
			return candidate, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}

	return "", fmt.Errorf("no kg/ directory found (set OYT_KB_PATH or run from a project with kg/)")
}

// List returns all entries in the KB, grouped by category.
func (k *KB) List() ([]Entry, error) {
	var entries []Entry

	err := filepath.Walk(k.Root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() || !strings.HasSuffix(info.Name(), ".md") {
			return nil
		}
		if info.Name() == "README.md" {
			return nil
		}

		rel, _ := filepath.Rel(k.Root, path)
		parts := strings.SplitN(rel, string(os.PathSeparator), 2)

		category := parts[0]
		name := strings.TrimSuffix(filepath.Base(rel), ".md")

		entries = append(entries, Entry{
			Path:     strings.TrimSuffix(rel, ".md"),
			Category: category,
			Name:     name,
		})
		return nil
	})

	return entries, err
}

// Get reads a specific entry by path (e.g. "catalog/ingestion").
func (k *KB) Get(entryPath string) (*Entry, error) {
	fullPath := filepath.Join(k.Root, entryPath+".md")
	data, err := os.ReadFile(fullPath)
	if err != nil {
		return nil, fmt.Errorf("entry not found: %s", entryPath)
	}

	parts := strings.SplitN(entryPath, string(os.PathSeparator), 2)
	category := parts[0]
	name := filepath.Base(entryPath)

	return &Entry{
		Path:     entryPath,
		Category: category,
		Name:     name,
		Content:  string(data),
	}, nil
}

// Evaluate checks a proposal against the KB catalog and principles.
func (k *KB) Evaluate(proposal string) (*Result, error) {
	items, err := k.parseCatalog()
	if err != nil {
		return nil, err
	}

	proposalL := strings.ToLower(proposal)
	var matched []MatchedItem
	var conflicts []Conflict
	highestTier := 0

	for _, item := range items {
		if !strings.Contains(proposalL, strings.ToLower(item.solution)) {
			continue
		}

		matched = append(matched, MatchedItem{
			Solution:       item.solution,
			Recommendation: item.recommendation,
			Qualifier:      item.qualifier,
			Category:       item.category,
			Context:        item.context,
		})

		recL := strings.ToLower(item.recommendation)
		if strings.Contains(recL, "reject") {
			if highestTier < 1 {
				highestTier = 1
			}
			var alts []string
			for _, other := range items {
				if other.category == item.category && strings.Contains(strings.ToLower(other.recommendation), "strong default") {
					alts = append(alts, other.solution)
				}
			}
			conflicts = append(conflicts, Conflict{
				Tier:         1,
				Source:       "catalog/" + item.category,
				Message:      item.solution + ": Rejected. " + item.context,
				Alternatives: alts,
			})
		} else if strings.Contains(recL, "avoid") {
			if highestTier < 2 {
				highestTier = 2
			}
			conflicts = append(conflicts, Conflict{
				Tier:    2,
				Source:  "catalog/" + item.category,
				Message: item.solution + ": Avoid. " + item.context,
			})
		}
	}

	approved := highestTier != 1

	var rec string
	switch {
	case len(matched) == 0:
		rec = "No catalog match. Verify against Tier 1: EU sovereignty, open source, local-first."
	case highestTier == 0:
		var names []string
		for _, m := range matched {
			names = append(names, m.Solution)
		}
		rec = "Approved. " + strings.Join(names, ", ") + " aligns with KB recommendations."
	case highestTier == 1:
		var msgs []string
		for _, c := range conflicts {
			msgs = append(msgs, c.Message)
		}
		rec = "REJECTED (Tier 1 violation). " + strings.Join(msgs, " ")
		var allAlts []string
		for _, c := range conflicts {
			allAlts = append(allAlts, c.Alternatives...)
		}
		if len(allAlts) > 0 {
			rec += " Use instead: " + strings.Join(allAlts, ", ") + "."
		}
	default:
		var msgs []string
		for _, c := range conflicts {
			msgs = append(msgs, c.Message)
		}
		rec = "WARNING (Tier 2 deviation). " + strings.Join(msgs, " ")
	}

	return &Result{
		Approved:       approved,
		Tier:           highestTier,
		Conflicts:      conflicts,
		Recommendation: rec,
		MatchedItems:   matched,
	}, nil
}

// parseCatalog reads all catalog entries and extracts table rows.
func (k *KB) parseCatalog() ([]catalogItem, error) {
	entries, err := k.List()
	if err != nil {
		return nil, err
	}

	var items []catalogItem
	for _, e := range entries {
		if e.Category != "catalog" {
			continue
		}
		full, err := k.Get(e.Path)
		if err != nil {
			continue
		}

		inTable := false
		recCol := -1

		for _, line := range strings.Split(full.Content, "\n") {
			if !inTable {
				if strings.Contains(line, "|") && strings.Contains(line, "Recommendation") {
					cols := strings.Split(line, "|")
					for i, c := range cols {
						if strings.Contains(c, "Recommendation") {
							recCol = i
							break
						}
					}
					inTable = true
				}
				continue
			}

			// Skip separator rows
			trimmed := strings.TrimSpace(line)
			if len(trimmed) > 0 && trimmed[0] == '|' {
				stripped := strings.Trim(trimmed, "| ")
				if len(stripped) > 0 && strings.Count(stripped, "-")+strings.Count(stripped, " ")+strings.Count(stripped, "|") == len(stripped) {
					continue
				}
			}

			if !strings.Contains(line, "|") || strings.TrimSpace(line) == "" {
				inTable = false
				continue
			}

			cols := strings.Split(line, "|")
			if len(cols) < 3 {
				continue
			}

			solution := strings.TrimSpace(cols[1])
			solution = strings.ReplaceAll(solution, "**", "")

			rawRec := ""
			if recCol >= 0 && recCol < len(cols) {
				rawRec = strings.TrimSpace(cols[recCol])
			}
			ctx := ""
			if recCol+1 < len(cols) {
				ctx = strings.TrimSpace(cols[recCol+1])
			}

			rec := rawRec
			qual := ""
			if idx := strings.Index(rawRec, "("); idx >= 0 {
				if end := strings.Index(rawRec[idx:], ")"); end >= 0 {
					rec = strings.TrimSpace(rawRec[:idx])
					qual = rawRec[idx+1 : idx+end]
				}
			}

			if solution != "" {
				items = append(items, catalogItem{
					category:       e.Name,
					solution:       solution,
					recommendation: rec,
					qualifier:      qual,
					context:        ctx,
				})
			}
		}
	}

	return items, nil
}
