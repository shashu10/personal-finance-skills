# Working inside a larger private workspace

Readers can install through a prompt or `npx skills add`, as shown in the README.
The commands here are for agents and contributors maintaining a local checkout. To
set up the helpers after installing the skills, follow the
[agent runtime instructions](../skills/finance-setup/references/runtime.md).

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
The installer does not migrate existing personal ledgers. Preserve their originals,
translate one account at a time to the documented import format, and reconcile before
using a new snapshot for planning. Never apply the demo over existing records.

An existing private project can record its integration in the selected workspace's
`setup.md` and applicable `AGENTS.md`. Follow the
[project integration guide](../skills/finance-setup/references/project.md) for runtime,
account-import, research, and dashboard discovery. Those adapters belong to the host
project; their paths and private configuration do not belong in the public skills.

The `finance-dashboard` skill can inspect an existing local dashboard and its documented
read-only status/report interfaces. This repository distributes the skill, not a dashboard
application. Adding the seventh skill to an existing linked installation preserves the
six matching links; the installer creates only the missing link. Existing copies still
require deliberate replacement because the installer does not overwrite files.

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

The public-source check examines the indexed tree. An optional `--denylist` takes a
private text file of literal values to detect without printing them. Keep that file
outside this repo.
Schema and behavior tests use synthetic temporary workspaces and require no broker login,
market-data subscription, or model API key.

The bundled plugin manifest and skills installers distribute the skills; they do not
automatically configure broker MCP servers or install Python dependencies. The setup
skill handles those runtime prerequisites. The local-folder installer remains useful
for linked development. Optional research packages are installed in separate virtual
environments at recorded upstream revisions; update pins deliberately and re-test.
