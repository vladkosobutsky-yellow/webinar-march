#!/usr/bin/env python3
"""Detect missing app tests (heuristic) and pytest-cov gaps; drive Cursor CLI agent in CI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _github_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        if "\n" in value:
            delim = "MISSING_TESTS_EOF"
            f.write(f"{name}<<{delim}\n{value}\n{delim}\n")
        else:
            f.write(f"{name}={value}\n")


def _module_candidates(rel: Path) -> list[Path]:
    name = rel.parts[-1]
    tests = Path("tests")
    out = [tests / f"test_{name}.py"]
    if len(rel.parts) > 1:
        out.append(tests.joinpath(*rel.parts[:-1]) / f"test_{name}.py")
    return out


def _tests_reference_module(tests_dir: Path, rel: Path) -> bool:
    mod = "app." + ".".join(rel.parts)
    mod_file = "app/" + "/".join(rel.parts) + ".py"
    prefix = rel.parts[0]
    for t in tests_dir.rglob("*.py"):
        try:
            text = t.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if mod in text or mod_file in text:
            return True
        if f"from app.{prefix}" in text or f"import app.{prefix}" in text:
            if len(rel.parts) == 1:
                return True
    return False


def _missing_modules(root: Path, app: Path, tests_dir: Path) -> list[str]:
    missing: list[str] = []
    for py in sorted(app.rglob("*.py")):
        if py.name == "__init__.py":
            continue
        rel = py.relative_to(app).with_suffix("")
        if any(c.is_file() for c in _module_candidates(rel)):
            continue
        if tests_dir.is_dir() and _tests_reference_module(tests_dir, rel):
            continue
        missing.append(str(py.relative_to(root)))
    return missing


def _run_pytest_cov(root: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["uv", "run", "pytest", "-q"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except FileNotFoundError:
        return False, "error: `uv` not found; install uv and run this script from the repository root.\n"
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode == 0, out


def main() -> None:
    root = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
    os.chdir(root)
    app = root / "app"
    tests_dir = root / "tests"

    missing: list[str] = []
    cov_ok = True
    cov_text = ""

    if not app.is_dir():
        _github_output("found", "false")
        print("No app/ directory; skipping.")
        return

    missing = _missing_modules(root, app, tests_dir)
    cov_ok, cov_text = _run_pytest_cov(root)

    found = bool(missing) or not cov_ok

    if not found:
        _github_output("found", "false")
        for name in ("cursor-agent-prompt.txt", "missing-modules.txt", "coverage-report.txt"):
            p = root / name
            if p.is_file():
                p.unlink()
        print("All app modules have corresponding tests (heuristic) and pytest-cov passed.")
        return

    _github_output("found", "true")

    mod_lines = "\n".join(f"- `{m}`" for m in missing) if missing else ""
    summary_bits: list[str] = []
    if missing:
        summary_bits.append(mod_lines)
    if not cov_ok:
        summary_bits.append("- `pytest-cov`: threshold or tests failed (see `coverage-report.txt`)")
    summary = "\n".join(summary_bits)
    _github_output("modules", summary)

    print("CI: test gaps detected.")
    if missing:
        print("Missing test modules (heuristic):\n" + mod_lines)
    if not cov_ok:
        print("pytest-cov / pytest output:\n" + cov_text)

    (root / "missing-modules.txt").write_text(summary + "\n", encoding="utf-8")
    (root / "coverage-report.txt").write_text(cov_text, encoding="utf-8")

    sections: list[str] = [
        "This is a Python package under `app/` using pytest with pytest-cov "
        "(`uv run pytest`, tests under `tests/`). Coverage is configured in `pyproject.toml` "
        "(`tool.coverage.*`, `tool.pytest.ini_options`).",
        "",
    ]
    if missing:
        sections.extend(
            [
                "These application files have no obvious matching test module "
                "(no `tests/test_<name>.py` or mirrored path, and no test file referencing the module):",
                "",
                mod_lines,
                "",
            ]
        )
    if not cov_ok:
        sections.extend(
            [
                "pytest (including pytest-cov) did not succeed. Full output:",
                "",
                "```text",
                cov_text.rstrip(),
                "```",
                "",
                "After adding tests, `uv run pytest` must pass and meet the coverage `fail_under` setting. "
                "Machine-readable line data is written to `coverage.json` at the repo root when pytest runs.",
                "",
            ]
        )
    sections.extend(
        [
            "Add or extend pytest tests so behavior is covered. Follow patterns in existing tests, "
            "keep cases small and deterministic, and do not use `eval()`/`exec()` for calculator logic.",
            "",
            "IMPORTANT — CI restrictions: Do not run git, gh, branch, commit, push, or open PRs. "
            "Do not change files under app/; only add or edit files under tests/. "
            "The workflow will commit and open the PR. You may run `uv run pytest` to verify.",
        ]
    )
    prompt = "\n".join(sections)
    (root / "cursor-agent-prompt.txt").write_text(prompt, encoding="utf-8")


if __name__ == "__main__":
    main()
    sys.exit(0)
