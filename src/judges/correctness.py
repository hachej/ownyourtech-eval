"""Ground truth CSV comparison judge.

Compares agent output against expected CSVs — pass/fail per model per column.
"""

import csv
import math
import subprocess
from pathlib import Path


def load_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def vectors_match(v1, v2, tol=1e-2):
    if len(v1) != len(v2):
        return False, f"row count mismatch: expected {len(v1)}, got {len(v2)}"

    mismatches = 0
    for a, b in zip(v1, v2):
        if (a is None or a == "") and (b is None or b == ""):
            continue
        if (a is None or a == "") != (b is None or b == ""):
            mismatches += 1
            continue
        try:
            fa, fb = float(a), float(b)
            if math.isnan(fa) and math.isnan(fb):
                continue
            if fa != 0 and abs(fb - fa) / abs(fa) > tol:
                mismatches += 1
            elif fa == 0 and fb != 0:
                mismatches += 1
        except (ValueError, TypeError):
            if str(a).strip() != str(b).strip():
                mismatches += 1

    if mismatches > 0:
        return False, f"{mismatches}/{len(v1)} values differ"
    return True, "ok"


def export_from_duckdb(workdir, model_names):
    """Export tables from DuckDB to CSVs. Searches all db files and all schemas."""
    import glob
    db_files = glob.glob(str(Path(workdir) / "**/*.duckdb"), recursive=True)
    if not db_files:
        return None

    output_dir = Path(workdir) / "_judge_output"
    output_dir.mkdir(exist_ok=True)

    for name in model_names:
        out = output_dir / f"{name}.csv"
        if out.exists():
            continue
        for db_file in db_files:
            if out.exists():
                break
            # Try main schema first
            try:
                result = subprocess.run(
                    ["duckdb", db_file, "-csv", f"SELECT * FROM {name} ORDER BY 1,2;"],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    out.write_text(result.stdout)
                    continue
            except Exception:
                pass
            # Search all schemas for the table
            search_query = (
                f"SELECT table_schema FROM information_schema.tables "
                f"WHERE table_name = '{name}' "
                f"AND table_schema NOT IN ('information_schema', 'pg_catalog') "
                f"LIMIT 1;"
            )
            try:
                schema_result = subprocess.run(
                    ["duckdb", db_file, "-noheader", "-csv", search_query],
                    capture_output=True, text=True, timeout=30,
                )
                if schema_result.returncode == 0 and schema_result.stdout.strip():
                    schema = schema_result.stdout.strip()
                    result = subprocess.run(
                        ["duckdb", db_file, "-csv",
                         f'SELECT * FROM "{schema}"."{name}" ORDER BY 1,2;'],
                        capture_output=True, text=True, timeout=30,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        out.write_text(result.stdout)
            except Exception:
                pass

    return output_dir


def export_from_sqlite(workdir, model_names):
    """Export tables from SQLite to CSVs."""
    import glob
    db_files = glob.glob(str(Path(workdir) / "**/*.sqlite"), recursive=True) + glob.glob(str(Path(workdir) / "**/*.db"), recursive=True)
    if not db_files:
        return None

    db_file = db_files[0]
    output_dir = Path(workdir) / "_judge_output"
    output_dir.mkdir(exist_ok=True)

    for name in model_names:
        out = output_dir / f"{name}.csv"
        try:
            result = subprocess.run(
                ["sqlite3", "-header", "-csv", db_file, f'SELECT * FROM "{name}" ORDER BY 1,2;'],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                out.write_text(result.stdout)
        except Exception:
            pass

    return output_dir


def judge(ctx: dict) -> dict:
    scenario_dir = Path(ctx["scenario_dir"])
    scenario = ctx["scenario"]
    workdir = Path(ctx["workdir"])

    models = scenario.get("expected_models", [])
    model_names = [m["name"] for m in models]

    # Export agent output
    output_dir = export_from_duckdb(workdir, model_names)
    if output_dir is None:
        output_dir = export_from_sqlite(workdir, model_names)
    if output_dir is None:
        return {
            "pass": False,
            "summary": "(no database found in workdir)",
            "model_results": {m: {"pass": False, "error": "no database"} for m in model_names},
        }

    total = len(models)
    passed = 0
    model_results = {}

    for model in models:
        name = model["name"]
        gt_path = (scenario_dir / model["ground_truth"]).resolve()
        output_path = output_dir / f"{name}.csv"

        if not gt_path.exists():
            model_results[name] = {"pass": False, "error": "ground truth not found"}
            continue
        if not output_path.exists():
            model_results[name] = {"pass": False, "error": "output not found"}
            continue

        gt_rows, gt_cols = load_csv(gt_path)
        out_rows, out_cols = load_csv(output_path)

        if not gt_cols:
            model_results[name] = {"pass": False, "error": "ground truth has no columns"}
            continue

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
        if all_pass:
            passed += 1

        model_results[name] = {
            "pass": all_pass,
            "matched": len(matched),
            "unmatched": len(unmatched),
            "missing": len(missing),
            "gt_rows": len(gt_rows),
            "out_rows": len(out_rows),
        }

    return {
        "pass": passed == total,
        "summary": f"({passed}/{total} models correct)",
        "model_results": model_results,
    }
