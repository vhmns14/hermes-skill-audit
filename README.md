# Hermes Skill Audit

[![CI](https://github.com/vhmns14/hermes-skill-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/vhmns14/hermes-skill-audit/actions/workflows/ci.yml)

A tiny, dependency-free CLI that scans **Hermes Agent** and **OpenClaw** skill/plugin folders for supply-chain risks:

- 🔥 Destructive commands (`rm -rf`, `mkfs`, …)
- 📥 Piping downloads straight into a shell (`curl … | sh`)
- 🔓 Privilege escalation (`sudo`, `chmod 777`)
- 🕵️ Obfuscation (`base64 -d`, `eval`, `python -c … exec`)
- 📤 Possible data exfiltration (outbound POST)
- 🧠 Prompt-injection text inside skill markdown

Skills are user-contributed and largely **unvetted** (ClawHub, agentskills.io), so auditing them before use is a real safety win.

## Install

No dependencies — just Python 3.

```bash
git clone https://github.com/vhmns14/hermes-skill-audit
cd hermes-skill-audit
```

## Usage

```bash
# Audit one or more skill directories/files
python audit.py path/to/skill

# Custom rules + JSON report
python audit.py skills/ --rules rules.json --json report.json

# Don't fail the shell on HIGH findings (still prints them)
python audit.py skills/ --no-fail
```

Exit code is `1` if any **HIGH** severity issue is found (handy in CI).

## How it works

Rules live in [`rules.json`](rules.json) as `{id, severity, description, pattern}` entries (regex, case-insensitive). `audit.py` walks the target, matches each rule against file contents, and reports hits with file + line + the offending snippet.

Add your own rules by dropping entries into `rules.json`.

## Example

See [`examples/risky-skill`](examples/risky-skill) (contains intentional findings) and [`examples/clean-skill`](examples/clean-skill).

## License

MIT
