# Use an existing private project

Read the active project's applicable `AGENTS.md` and the selected private workspace's
`setup.md` before installing another runtime. Follow the configuration paths they name,
such as `config/finance_skills.json`, and inspect documented commands with `--help`.
Do not assume a neighboring checkout, dashboard, or brokerage profile belongs to this task.

Keep the project's original records and the normalized finance workspace separate.
A project adapter can translate records deliberately; setup and a status check do not
authorize an import or establish that account data is current. Never point initialization
at an existing directory of records in another format.

## Record the integration

Save the selected project root, configuration path, interpreter, workspace, and base
currency in private `setup.md`. Record supported commands for status, initialization,
explicit imports, validation, and summaries. If available, also record research modes,
their provider and sharing rules, report locations, and the dashboard's local URL,
startup command, and read-only status endpoint. Keep credentials out of the note.

Some private projects expose commands like these. They are host-project adapters,
not files supplied by the public skills bundle. Run them only after verifying that
the selected project documents and implements them:

```text
python scripts/finance.py status
python scripts/finance.py init
python scripts/finance.py import-project
python scripts/finance.py validate
python scripts/finance.py summary
python scripts/run_skill_research.py EXAMPLE --mode technical --dry-run
python scripts/run_skill_research.py EXAMPLE --mode fundamental --dry-run
python scripts/run_skill_research.py EXAMPLE --mode both --dry-run
```

Here `python` is the selected environment's absolute interpreter, the working directory
is the verified private project root, and `EXAMPLE` is an illustrative ticker. The project
configuration may select a workspace such as `data/finance-workspace`; resolve that path
against the documented project root, outside the public source checkout.

Use the status result to check configuration and paths before changing records.
Run an import only for an authorized account refresh or migration, preserve the source
evidence, and reconcile the imported snapshot. A local file import does not prove that
the source came from a fresh brokerage read. Continue to use `finance-core` directly
for operations the project adapter does not expose.

## Research and dashboard boundaries

A project may route technical work through TradingAgents and fundamental work through
Vibe-Trading. Inspect the configured mode and dry-run result before a live run. Preserve
the project's existing context and risk checks, the workspace's sharing permissions,
and the user's authorization for the selected model provider. Do not switch to an older
script to evade a missing-data or sharing error. Ticker-only research need not include
personal records.

Read an existing dashboard through its documented local interface. A project may expose
`GET /api/skills` for workspace status and report metadata; that route is not part of
`finance-core`. Loading the page or reading status must not be described as importing
accounts or generating research. Check source dates separately from page refresh times.

Keep scheduling separate from a single research run. Reuse a schedule only when it is
already configured for this workflow, or create one when the user requests recurrence.
Installing skills does not create a daily job, provide a dashboard, or publish a site.
