# Personal Finance Skills

Six agent skills for gathering your accounts into a local ledger, researching
investments, working through financial decisions, and remembering what you decided.

Bring your own agent, accounts, and model provider. The shared Python helpers validate
records and calculate scenarios. You keep your financial workspace outside this source
repository. All examples here are synthetic.

| Skill | Ask it to… |
| --- | --- |
| [finance-setup](skills/finance-setup/SKILL.md) | Set up a workspace, inventory accounts, and learn the personal facts relevant to planning. |
| [finance-gather](skills/finance-gather/SKILL.md) | Gather accounts through available APIs, exports, or computer use and reconcile the ledger. |
| [investment-research](skills/investment-research/SKILL.md) | Research stocks and IPOs, fundamentals, technicals, and strategy evidence. |
| [portfolio-review](skills/portfolio-review/SKILL.md) | Review a proposed trade against your actual holdings, liquidity, and chosen limits. |
| [finance-plan](skills/finance-plan/SKILL.md) | Explain net worth and work through budgets, job changes, debt, and tax-sensitive scenarios. |
| [finance-memory](skills/finance-memory/SKILL.md) | Save confirmed decisions and facts, track corrections, and distinguish plans from completed actions. |

## Start locally

Requires Python 3.11+ for the core. Optional research integrations have their own Python
requirements. No broker or model credentials are needed for the demo.

```bash
git clone https://github.com/shashu10/personal-finance-skills.git
cd personal-finance-skills
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/install_skills.py --target "$HOME/.agents/skills"
```

The installer links the skills to this checkout, so edits stay in one place. Use
`--mode copy` if your host does not support links. For project-only Codex installation,
choose `/path/to/your/project/.agents/skills` as the target. The command refuses to
replace existing skills. Add this environment's `bin` directory to your agent's PATH,
or give the agent the absolute path to `.venv/bin/finance-core`.

The folders use the Agent Skills format. Codex supports `.agents/skills`; another host
may use a different discovery location or invocation syntax. Computer-use support and
broker tools must be available in that host. The repository also includes a Codex plugin
manifest; it does not bundle a browser or automatically authenticate any account.

Try the calculations using a new, explicitly synthetic workspace:

```bash
.venv/bin/finance-core init --workspace "$HOME/finance-demo" --demo
.venv/bin/finance-core validate --workspace "$HOME/finance-demo"
.venv/bin/finance-core summary --workspace "$HOME/finance-demo"
.venv/bin/finance-core plan --workspace "$HOME/finance-demo" \
  --monthly-expenses 3200 --monthly-income 2000 --one-time-cost 1500
```

For your own records, choose a different directory and omit `--demo`:

```bash
.venv/bin/finance-core init --workspace "$HOME/my-finances" --base-currency USD
```

Then ask your agent:

> Use finance-setup with my private workspace. Ask only for the missing information
> needed to inventory my accounts and understand my goals.

> Use finance-gather to update my accounts. Prefer read-only APIs or statement exports;
> use computer use where needed. I'll handle logins. Show unresolved discrepancies.

> Use portfolio-review to assess this proposed investment against my current holdings
> and rules, then use finance-memory to record only the decisions I confirm.

## What is implemented

- Six skill workflows, with references for onboarding, account gathering, research,
  proposals, planning, and memory.
- A dependency-free calculation core: private workspace initialization, normalized
  account imports, validation, reconciliation, summaries, cash runway scenarios,
  proposal checks, controlled context exports, and confirmed memory records.
- Synthetic fixtures, regression tests, a skill validator, and a public-source check.
- Optional pinned TradingAgents and Vibe-Trading installers, plus a TradingAgents runner
  using the upstream portfolio interface. See [integrations](docs/integrations.md).

Account gathering is agent-assisted. This release does not contain a universal bank
scraper, automatic broker synchronization service, or a built-in provider credential
manager. Existing broker tools provide connectivity; the skills normalize their results
through the shared import format. Coverage varies by provider and account type.

Technical, fundamental, IPO, and tax research are source-grounded agent workflows.
The core does not determine tax residency, prepare tax returns, certify a cost basis,
or supply market data. Unlisted securities may have no price history. Research outputs
are not evidence that a strategy will be profitable.

## One private workspace

| File | Purpose |
| --- | --- |
| `ledger.json` | Accounts, current positions, cash, liabilities, source dates, and FX evidence. |
| `transactions.json` / `lots.json` | Identified transaction and lot records; reimports do not duplicate identical records. |
| `facts.json` | User-confirmed personal facts, evidence, effective dates, and uncertainty. |
| `rules.json` | User-owned limits, freshness thresholds, and context sharing choices. |
| `decisions.json` | Confirmed decisions and supersession records, distinct from execution evidence. |

The skill can maintain a human-readable `decisions.md` and research journal in that
private workspace. These are not implicit end-of-session hooks or scheduled jobs;
invoke the memory workflow or configure your host's automation explicitly.

See the [data contract](docs/data-contract.md) for exact fields and commands. Monetary
values use decimal strings. Account identifiers are aliases. Unknown balances stay
unknown, and missing FX or stale sources appear as issues rather than invented values.
Reported net account totals are reconciled against positions plus cash minus liabilities.
Use `include_in_totals: false` for a parent statement already represented by child accounts.

Planning uses available unrestricted cash by default. Portfolio reviews assess scenarios
and flag limits; they do not block actions in your brokerage. Limits start unset. No
skill can choose your risk tolerance for you, and no order execution or money-transfer
interface is included.

## Privacy and sharing

Local storage is not local inference. An agent can send the files it reads or screenshots
it sees to its model provider. The explicit context exporters start disabled; enable
only the sharing mode you want. This does not restrict an agent's own filesystem tools.
See [privacy and data flow](docs/privacy.md).

Keep passwords, API keys, tokens, full account numbers, statements, tax returns, and real
ledgers out of this repository. Use a keychain or a supported credential store. The user
handles authentication; read-only provider permissions are preferable where available.

## Develop inside a larger project

The repository can live inside a private multi-repo workspace. Link its skills into the
parent project and keep the public Git boundary here. [Development instructions](docs/development.md)
cover editable installs, local links, synthetic tests, and pre-publication checks.

This is a v0.1 research and planning toolkit, not a regulated advisory service or an
automated trader. Review consequential financial and tax decisions using the underlying
sources and appropriate professional advice.

Original code and skills: [MIT license](LICENSE). Optional upstream integrations retain
their own licenses; see [attribution](NOTICE.md).
