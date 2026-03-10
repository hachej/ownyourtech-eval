"""Standalone ground truth comparison.

Usage:
    python check.py <scenario-dir> <output-dir>

output-dir should contain CSVs named <model>.csv
"""

import sys
from pathlib import Path

import yaml

from correctness import load_csv, vectors_match


def check_model(model_name, gt_path, output_path):
    """Compare one model against ground truth. Returns (pass, details)."""
    if not gt_path.exists():
        return False, {"error": f"ground truth not found: {gt_path}"}

    if not output_path.exists():
        return False, {"error": f"output not found: {output_path}"}

    gt_rows, gt_cols = load_csv(gt_path)
    out_rows, out_cols = load_csv(output_path)

    if not gt_cols:
        return False, {"error": "ground truth has no columns"}

    out_col_map = {c.upper(): c for c in out_cols} if out_cols else {}

    matched = []
    unmatched = []
    missing = []

    for col in gt_cols:
        out_col = out_col_map.get(col.upper())
        if out_col is None:
            missing.append(col)
            continue

        gt_values = [row.get(col) for row in gt_rows]
        out_values = [row.get(out_col) for row in out_rows]

        ok, reason = vectors_match(gt_values, out_values)
        if ok:
            matched.append(col)
        else:
            unmatched.append({"column": col, "reason": reason})

    all_pass = len(missing) == 0 and len(unmatched) == 0
    return all_pass, {
        "matched": matched,
        "unmatched": unmatched,
        "missing": missing,
        "gt_rows": len(gt_rows),
        "out_rows": len(out_rows),
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python check.py <scenario-dir> <output-dir>")
        print("  output-dir should contain CSVs named <model>.csv")
        sys.exit(1)

    scenario_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    with open(scenario_dir / "scenario.yaml") as f:
        scenario = yaml.safe_load(f)

    models = scenario.get("expected_models", [])
    if not models:
        print("No expected_models in scenario.yaml")
        sys.exit(1)

    total = len(models)
    passed = 0
    failed = 0

    print(f"=== Check: {scenario['name']} ===")
    print(f"Models: {total}")
    print()

    for model in models:
        name = model["name"]
        gt_path = (scenario_dir / model["ground_truth"]).resolve()
        output_path = output_dir / f"{name}.csv"

        ok, details = check_model(name, gt_path, output_path)

        if ok:
            matched_count = len(details["matched"])
            print(f"PASS  {name}  ({matched_count} columns, {details['gt_rows']} rows)")
            passed += 1
        else:
            if "error" in details:
                print(f"FAIL  {name}  ({details['error']})")
            else:
                matched_count = len(details["matched"])
                missing_count = len(details["missing"])
                unmatched_count = len(details["unmatched"])
                print(f"FAIL  {name}  (matched={matched_count}, unmatched={unmatched_count}, missing={missing_count})")
                if details["gt_rows"] != details["out_rows"]:
                    print(f"      rows: expected={details['gt_rows']}, got={details['out_rows']}")
                for u in details["unmatched"]:
                    print(f"      column {u['column']}: {u['reason']}")
                for m in details["missing"]:
                    print(f"      column {m}: MISSING")
            failed += 1

    print()
    print(f"=== Results ===")
    print(f"PASS: {passed}/{total}")
    print(f"FAIL: {failed}/{total}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
