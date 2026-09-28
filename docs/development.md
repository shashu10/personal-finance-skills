# Working inside a larger private workspace

This repository can be a child directory of a private project containing other repos.
It has its own `.git` boundary. Use `git -C /path/to/personal-finance-skills ...` for
all Git operations. Do not initialize or stage the parent workspace.

Install the runtime into the interpreter you want to use, then link the skills into
the parent's discovery directory:

```bash
/path/to/python -m pip install --no-deps -e /path/to/personal-finance-skills
/path/to/python /path/to/personal-finance-skills/scripts/install_skills.py \
  --target /path/to/private-project/.agents/skills
```

Links keep one editable copy of each skill. The installer checks all target names before
writing and refuses to overwrite existing skills. Start a new chat if the host does not
pick up new skills. Editing a skill does not require copying private records into it.

Select a separate private workspace with `--workspace` or `FINANCE_WORKSPACE`.
Existing personal ledgers are not migrated automatically. Preserve their originals,
translate one account at a time to the documented import format, and reconcile before
using a new snapshot for planning. Never apply the demo over existing records.

## Development checks

```bash
python -m pip install -e '.[dev]'
python -m unittest discover -s tests -v
python scripts/validate_skills.py
git add AGENTS.md .gitignore .codex-plugin .github README.md LICENSE NOTICE.md \
  pyproject.toml integrations.json docs examples schemas scripts skills src tests
python scripts/check_public.py
git diff --cached --stat
```

The check examines the indexed tree. An optional `--denylist` takes a private text file
of literal values to detect without printing them. Keep that file outside this repo.
Schema/behavior tests use synthetic temporary workspaces and require no broker login,
market-data subscription, or model API key.

The bundled plugin manifest describes the skills; it does not automatically configure
broker MCP servers or install Python dependencies. The local-folder installer is the
tested development path. Optional research packages are installed in separate virtual
environments at recorded upstream revisions; update pins deliberately and re-test.
