---
name: finance-setup
description: Set up a private personal finance workspace, shared calculation runtime, and gradual account and household intake. Use for initial setup or missing prerequisites, not for routine investment research.
---

# Finance setup

Create a usable private workspace and explain what is known, missing, and connected.
Start with the user's immediate question; do not require a complete financial biography.
Run installation and calculation commands yourself with the host's tools. Keep
the conversation natural; do not hand the user a Python setup checklist.
Ask for help only when a required capability, permission, or login is unavailable.

Before collecting personal financial records, recommend turning off optional sharing
for model training or product improvement in the provider's privacy or data controls.
Ask the user to check their agent and every model provider it uses, including optional
research tools. Use current official guidance for the exact settings. Explain that the
provider still processes requests and may retain data even when training is disabled.

## Establish the runtime and workspace

1. Reuse the user's existing workspace and configured environment when known.
   Otherwise select a private directory outside the public source checkout and confirm
   the base currency. A new currency choice does not imply residence or nationality.
   Read the active project's applicable `AGENTS.md` and the selected workspace's
   `setup.md`, when present, for integration settings. If the project supplies account, research,
   or dashboard adapters, follow [project integration](references/project.md).
2. Reuse a working `finance-core` command when available. Otherwise follow
   [runtime setup](references/runtime.md) to obtain the official source and install
   its helpers in an isolated environment. A global skills install may contain only
   skill folders, so a missing source checkout is expected. You can fetch it when needed.
   Record the working runtime path for later skills; do not modify global PATH or
   unrelated environments merely to make a bare command available.
3. Initialize with `finance-core init --workspace /private/path --base-currency USD`,
   replacing the illustrative path and currency with the user's choices.
   Use `--demo` only when explicitly requesting synthetic demonstration data in a
   separate workspace. Demonstration records are never real-account fallbacks.
4. Read the initialized files and run `finance-core validate --workspace /private/path`.
   Record no passwords, recovery codes, authentication cookies, or API secrets in them.

## Interview gradually

Read [the intake guide](references/intake.md) when collecting profile or account facts.
Reuse established answers and ask only questions that affect the current task.
Let the user skip sensitive or unavailable information; skipped fields remain unknown.

Start with account coverage, the planning question, and desired reporting currency.
Then collect relevant income, expense, household, goals, and tax-jurisdiction facts.
Distinguish what the user said from an inference and from a researched legal conclusion.
Neither location nor payroll alone establishes citizenship or tax residence.

`facts.json` and `decisions.json` use append-only records with user confirmation and
sources. To save intake statements, use the envelope in the intake guide and
`finance-core memory --workspace /private/path --input /private/path/intake.json`.
Save explicit answers within the authorized intake without asking for the same
confirmation again. Leave unanswered questions in a private intake note.

## Configure only what is needed

Inventory institutions using stable aliases such as `main-brokerage`; real account
numbers belong only in private connector settings if required by a provider.
Prefer read APIs, then downloaded exports, then user-authorized computer use.
Initial authorization may require the user's own login and multifactor authentication.
Store secrets in an available keychain or secret manager, or environment variables.

Keep limits in `rules.json` unset unless the user supplies them. A null limit means
report only. Keep both model-sharing switches false until the user authorizes that
specific export. Export permission does not authorize arbitrary model transmission.
Explain that a hosted agent may send files it reads and pages it sees to its model
provider. Local storage and disabled context exports do not make that inference local.
Optional research engines and connectors are unnecessary for an initial ledger.
Install them only when the requested workflow needs them. Before installing, check
current official documentation for supported authentication and data coverage.

## Handoff

Save the runtime command and any selected project adapters in the private workspace's
`setup.md` for later agent sessions. Tell the user where their records live, the base
currency, and which accounts are covered.
Describe accounts as connected, awaiting export, or unknown; an empty ledger is not
a zero net worth. Identify the next useful missing input rather than a long questionnaire.
The workspace should contain `ledger.json`, `transactions.json`, `lots.json`,
`facts.json`, `rules.json`, and `decisions.json`; reports and evidence stay private too.
State whether validation passed, and never claim setup implies any account was synced.
