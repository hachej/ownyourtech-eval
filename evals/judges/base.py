"""Judge runner — handles both prompt (.md) and code (.py) judges."""

import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path


JUDGES_DIR = Path(__file__).parent


def resolve_judge(name: str) -> tuple[str, Path]:
    """Return (type, path) for a judge. Prompt (.md) takes priority over code (.py)."""
    md_path = JUDGES_DIR / f"{name}.md"
    py_path = JUDGES_DIR / f"{name}.py"

    if md_path.exists():
        return "prompt", md_path
    if py_path.exists():
        return "code", py_path
    return "missing", JUDGES_DIR / name


def collect_source_files(workdir: Path, max_lines: int = 3000) -> str:
    """Collect source files for prompt context."""
    parts = []
    total = 0

    for ext in ("*.py", "*.sql", "*.sh", "*.yaml", "*.yml", "*.toml", "*.md"):
        for f in sorted(Path(workdir).rglob(ext)):
            if any(skip in f.parts for skip in (".venv", "venv", "__pycache__", ".git")):
                continue
            if f.suffix in (".duckdb", ".parquet", ".db"):
                continue

            content = f.read_text(errors="replace")
            lines = content.count("\n")

            if total + lines > max_lines:
                remaining = max_lines - total
                if remaining > 10:
                    parts.append(f"### {f.relative_to(workdir)}\n```\n" +
                                 "\n".join(content.split("\n")[:remaining]) +
                                 "\n[...truncated]\n```\n")
                break

            parts.append(f"### {f.relative_to(workdir)}\n```\n{content}\n```\n")
            total += lines

    return "\n".join(parts)


def run_prompt_judge(name: str, prompt_path: Path, ctx: dict) -> dict:
    """Run a prompt-based judge via claude -p."""
    workdir = Path(ctx["workdir"])
    rubric = prompt_path.read_text()

    # Read spec
    spec_path = workdir / "SPEC.md"
    spec = spec_path.read_text() if spec_path.exists() else "(no spec found)"

    # Collect source
    source = collect_source_files(workdir)

    if not source.strip():
        return {"judge": name, "pass": False, "error": "no source files found in workdir"}

    # Build full prompt
    full_prompt = f"""## Spec (what the agent was asked to build)
{spec}

## Rubric
{rubric}

## Agent's Source Code
{source}

Score according to the rubric. Return ONLY the JSON object."""

    judge_config = ctx.get("judge_config", {})
    judge_model = judge_config.get("judge_model", "sonnet")

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            [
                "claude", "-p",
                "--dangerously-skip-permissions",
                "--model", judge_model,
                "--max-budget-usd", "1.00",
                "--no-session-persistence",
                full_prompt,
            ],
            capture_output=True, text=True, timeout=600, env=env,
        )

        raw = result.stdout.strip()

        # Save raw output
        results_dir = Path(ctx.get("results_dir", "/tmp"))
        (results_dir / f"judge_{name}.md").write_text(raw)

        # Parse JSON
        scores = parse_json_from_text(raw)
        if scores:
            return {"judge": name, **scores}
        else:
            return {"judge": name, "pass": False, "error": "could not parse JSON from judge",
                    "raw": raw[:500]}

    except subprocess.TimeoutExpired:
        return {"judge": name, "pass": False, "error": "judge timed out"}
    except FileNotFoundError:
        return {"judge": name, "pass": False, "error": "claude CLI not found"}
    except Exception as e:
        return {"judge": name, "pass": False, "error": str(e)}


def run_code_judge(name: str, code_path: Path, ctx: dict) -> dict:
    """Run a Python code judge."""
    spec = importlib.util.spec_from_file_location(f"judges.{name}", code_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if not hasattr(mod, "judge"):
        return {"judge": name, "pass": False, "error": f"{name}.py has no judge() function"}

    verdict = mod.judge(ctx)
    verdict.setdefault("judge", name)
    return verdict


def run_judges(ctx: dict, judge_names: list[str]) -> list[dict]:
    """Run a list of judges and return verdicts."""
    verdicts = []

    for name in judge_names:
        judge_type, path = resolve_judge(name)

        if judge_type == "missing":
            verdicts.append({"judge": name, "pass": False, "error": f"no {name}.md or {name}.py found"})
        elif judge_type == "prompt":
            verdicts.append(run_prompt_judge(name, path, ctx))
        elif judge_type == "code":
            try:
                verdicts.append(run_code_judge(name, path, ctx))
            except Exception as e:
                verdicts.append({"judge": name, "pass": False, "error": str(e)})

    return verdicts


def print_verdicts(verdicts: list[dict]):
    """Print verdicts in readable format."""
    for v in verdicts:
        status = "PASS" if v.get("pass") else "FAIL"
        name = v.get("judge", "?")

        if "error" in v:
            print(f"  {status}  {name}  (error: {v['error']})")
            continue

        summary = v.get("summary", "")
        total = v.get("total")
        max_total = v.get("max_total")
        if total is not None and max_total is not None:
            summary = f"({total}/{max_total}) {summary}"

        print(f"  {status}  {name}  {summary}")

        # Print dimension scores if present
        for key, val in v.items():
            if isinstance(val, dict) and "score" in val and "max" in val:
                print(f"         {key}: {val['score']}/{val['max']}")


def parse_json_from_text(text: str) -> dict | None:
    """Extract JSON from LLM output."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    for pattern in [r"```json\s*\n(.*?)\n```", r"```\s*\n(\{.*?\})\n```", r"(\{[^{}]*\"pass\"[^{}]*\})"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue

    return None
