# Personal Finance Skills

Seven skills that help your AI agent gather your account records, research investments,
plan your finances, remember what you decide, and use an existing finance dashboard.

## Install

Paste this into Codex, Claude Code, or another agent that can install skills and run
local tools:

```text
Install all seven personal finance skills globally from https://github.com/shashu10/personal-finance-skills
```

Or install them from your terminal:

```bash
npx skills add shashu10/personal-finance-skills --global
```

Select all seven skills and your preferred agent when prompted.

## Start with a prompt

After installing, tell your agent:

> Use finance-setup to set up my personal finance workspace. Handle the technical
> setup for me, then ask what you need to know about my accounts and goals.

The agent installs the calculation helpers and creates a private folder for your
records. You provide the information and handle account logins. Computer use and
broker connections depend on the tools available in your agent.

To try it with sample data, ask:

> Show me how this works with a sample household, without using my real accounts.

## What to ask

| Skill | Example prompt |
| --- | --- |
| [finance-setup](skills/finance-setup/SKILL.md) | "Set this up and learn what matters about my finances." |
| [finance-gather](skills/finance-gather/SKILL.md) | "Update my accounts and show my net worth, debts, and anything missing." |
| [investment-research](skills/investment-research/SKILL.md) | "Research this stock or IPO. Check the financials, valuation, and risks." |
| [portfolio-review](skills/portfolio-review/SKILL.md) | "How would this proposed purchase change my portfolio and concentration?" |
| [finance-plan](skills/finance-plan/SKILL.md) | "How long could I cover my expenses if I stopped working?" |
| [finance-memory](skills/finance-memory/SKILL.md) | "Remember what I decided, why, and what would change my mind." |
| [finance-dashboard](skills/finance-dashboard/SKILL.md) | "Open my local finance dashboard and check what is current or missing." |

You can also ask the agent to install and use TradingAgents for analyst debates or
Vibe-Trading for research and backtests. These are optional; the agent handles their
setup when needed. Model and data providers may charge for those runs.

If you already have a private finance project, the skills can reuse its runtime and
research commands. Setup records how to find them. The dashboard skill uses an existing
local dashboard; this repository does not include or host a web application.

## Your records and privacy

Your accounts, personal facts, limits, and decisions stay in a private folder outside
the public source code. The agent records sources and dates, flags missing or stale
information, and uses code for calculations. It keeps proposed trades separate from
decisions you confirmed and completed transactions.

Your agent may send files it reads and screens it sees to its model provider, even
when you store your records locally. Keep passwords and tokens in a supported credential
store. Read more about [privacy and data flow](docs/privacy.md).

Before loading personal financial records, open your provider's privacy or data controls
and turn off any optional sharing of your content for model training or product improvement.
Check the controls for your agent and every model provider it uses, including optional
research tools. The provider will still process your requests and may retain data even
when training is disabled.

This first release supports account gathering, research, and planning. Account coverage
depends on the available APIs, exports, and computer-use tools. It does not place trades
or file taxes. Check consequential decisions against the sources and get qualified help
where needed.

## For agents and contributors

Python setup and calculation commands are in the
[agent setup instructions](skills/finance-setup/references/runtime.md).
The [data contract](docs/data-contract.md), [optional integrations](docs/integrations.md),
and [development guide](docs/development.md) cover the implementation and tests.
All public examples use synthetic data.

Original code and skills: [MIT license](LICENSE). Optional integrations retain their
own licenses; see [attribution](NOTICE.md).
