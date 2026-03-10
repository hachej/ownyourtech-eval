"""Run judges for an eval run.

Usage:
    python run_judges.py <scenario-dir> <workdir> <results-dir> <model> [judge1,judge2,...]

If no judges specified, reads from scenario.yaml judges list.
Default: correctness,code_quality
"""

import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from judges.base import run_judges, print_verdicts


def main():
    if len(sys.argv) < 5:
        print("Usage: run_judges.py <scenario-dir> <workdir> <results-dir> <model> [judges]")
        sys.exit(1)

    scenario_dir = Path(sys.argv[1])
    workdir = Path(sys.argv[2])
    results_dir = Path(sys.argv[3])
    model = sys.argv[4]

    with open(scenario_dir / "scenario.yaml") as f:
        scenario = yaml.safe_load(f)

    # Which judges to run
    if len(sys.argv) > 5:
        judge_names = sys.argv[5].split(",")
    else:
        raw = scenario.get("judges", ["correctness", "code_quality"])
        judge_names = [j["name"] if isinstance(j, dict) else j for j in raw]

    # Build config map
    judge_configs = {}
    for j in scenario.get("judges", []):
        if isinstance(j, dict) and "config" in j:
            judge_configs[j["name"]] = j["config"]

    ctx = {
        "workdir": str(workdir),
        "agent_log": str(results_dir / "agent.log"),
        "scenario_dir": str(scenario_dir),
        "scenario": scenario,
        "results_dir": str(results_dir),
        "model": model,
    }

    print(f"=== Judges: {', '.join(judge_names)} ===")
    print()

    # Run judges, injecting per-judge config
    all_verdicts = []
    for name in judge_names:
        judge_ctx = dict(ctx)
        if name in judge_configs:
            judge_ctx["judge_config"] = judge_configs[name]
        all_verdicts.extend(run_judges(judge_ctx, [name]))

    print_verdicts(all_verdicts)
    print()

    # Save verdicts
    clean = []
    for v in all_verdicts:
        c = {}
        for k, val in v.items():
            try:
                json.dumps(val)
                c[k] = val
            except (TypeError, ValueError):
                c[k] = str(val)
        clean.append(c)

    with open(Path(results_dir) / "verdicts.json", "w") as f:
        json.dump(clean, f, indent=2)

    passed = sum(1 for v in all_verdicts if v.get("pass"))
    print(f"=== Judge Results ===")
    print(f"PASS: {passed}/{len(all_verdicts)}")
    print(f"FAIL: {len(all_verdicts) - passed}/{len(all_verdicts)}")

    sys.exit(0 if passed == len(all_verdicts) else 1)


if __name__ == "__main__":
    main()
