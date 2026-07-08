#!/usr/bin/env python3
"""hermes-skill-audit — scan Hermes / OpenClaw skill folders for risky patterns.

Usage:
    python audit.py PATH [PATH ...] [--rules rules.json] [--json out.json] [--strict]

Exit code is 1 if any HIGH severity finding is present (unless --no-fail).
"""
import argparse
import json
import os
import re
import sys

DEFAULT_RULES = os.path.join(os.path.dirname(__file__), "rules.json")
SKILL_EXTS = (".md", ".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml", ".toml")


def load_rules(path):
    with open(path) as f:
        return json.load(f)["rules"]


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
        else:
            for root, _, files in os.walk(p):
                for name in files:
                    if name.lower().endswith(SKILL_EXTS):
                        yield os.path.join(root, name)


def scan_file(path, rules):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return []
    findings = []
    for rule in rules:
        try:
            rx = re.compile(rule["pattern"], re.IGNORECASE)
        except re.error:
            continue
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            findings.append(
                {
                    "rule": rule["id"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "file": path,
                    "line": line,
                    "match": m.group(0)[:120],
                }
            )
    return findings


def main():
    ap = argparse.ArgumentParser(description="Audit Hermes/OpenClaw skills for risks")
    ap.add_argument("paths", nargs="+", help="skill file or directory")
    ap.add_argument("--rules", default=DEFAULT_RULES)
    ap.add_argument("--json", help="write JSON report to this path")
    ap.add_argument("--no-fail", action="store_true", help="always exit 0")
    args = ap.parse_args()

    rules = load_rules(args.rules)
    findings = []
    for path in iter_files(args.paths):
        findings.extend(scan_file(path, rules))

    severity_rank = {"high": 3, "medium": 2, "low": 1}
    findings.sort(key=lambda x: -severity_rank.get(x["severity"], 0))

    if args.json:
        out_dir = os.path.dirname(os.path.abspath(args.json))
        os.makedirs(out_dir, exist_ok=True)
        with open(args.json, "w") as f:
            json.dump({"findings": findings, "count": len(findings)}, f, indent=2)

    if not findings:
        print("OK: no risky patterns found.")
        return 0

    by_sev = {}
    for fnd in findings:
        by_sev[fnd["severity"]] = by_sev.get(fnd["severity"], 0) + 1
    print(f"Found {len(findings)} issue(s): " + ", ".join(
        f"{v} {k}" for k, v in sorted(by_sev.items(), key=lambda x: -severity_rank[x[0]])))
    print("-" * 60)
    for fnd in findings:
        print(f"[{fnd['severity'].upper():6}] {fnd['rule']}  {fnd['file']}:{fnd['line']}")
        print(f"          {fnd['description']} -> {fnd['match']!r}")
    print("-" * 60)

    if args.no_fail:
        return 0
    return 1 if any(f["severity"] == "high" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
