# Optional research tools and account sources

The core ledger works without a brokerage connection, model API, or optional research
package. This project supplies an installer and a portfolio-aware TradingAgents runner.
It does not include live brokerage adapters or a universal browser scraper. The skills
guide an agent to collect data through an available connector, computer-use tool, or
statement import and save it in the same ledger. For each source, authenticate, check
which accounts it covers, and reconcile the results.

## Install an optional tool

Use Python 3.12 or newer. Run from this public checkout; replace the external paths below
with your own. Each tool needs a separate environment because their dependencies differ.

```sh
python3.12 scripts/install_optional.py --tool tradingagents --venv ~/finance-tools/tradingagents --dry-run
python3.12 scripts/install_optional.py --tool tradingagents --venv ~/finance-tools/tradingagents
python3.12 scripts/install_optional.py --tool vibe-trading --venv ~/finance-tools/vibe-trading --dry-run
python3.12 scripts/install_optional.py --tool vibe-trading --venv ~/finance-tools/vibe-trading
```

The installer refuses environments inside this checkout, existing unmanaged directories,
and using one tool's environment for the other. It installs the full Git revision in
[`integrations.json`](../integrations.json), runs `pip check`, and checks installed VCS
metadata. Re-running it can repair its own managed environment. It never logs into a broker
or starts a model. Source revisions are pinned; transitive dependencies are not locked.
The offline tests do not exercise optional installs or live upstream integrations.

The revisions were checked on September 27, 2026:

| Tool | Source pin | License |
|---|---|---|
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | `35543d0248bf89fcb92b17a15858ad0c0e940687` (0.5.1) | [Apache-2.0](https://github.com/TauricResearch/TradingAgents/blob/35543d0248bf89fcb92b17a15858ad0c0e940687/LICENSE) |
| [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | `0244eceaaf8d9e8ae79e2355836802acae3d1fc2` (0.1.15) | [MIT](https://github.com/HKUDS/Vibe-Trading/blob/0244eceaaf8d9e8ae79e2355836802acae3d1fc2/LICENSE) |

## Run portfolio-aware TradingAgents research

First initialize and reconcile your private workspace using the core CLI. In its
`rules.json`, explicitly set both `sharing.relative_context` and
`sharing.tradingagents_amounts` to `true` when you want
quantities and available average entry prices sent to the selected model provider.
`sharing.relative_context` alone does not grant this permission. No profile facts,
account identifiers, or credential values belong in this payload. Cash is exported as
`null`: balances across bank and retirement accounts do not establish cash available to
trade at a specific broker. Average entry price is included only when basis is known and
all holdings for that ticker use the ledger's base currency; otherwise it is omitted.

```sh
~/finance-tools/tradingagents/bin/python scripts/run_tradingagents.py --workspace ~/my-private-finances --ticker AAPL --dry-run
```

Dry-run prints the exact permitted portfolio JSON, requires no installed TradingAgents
package or model key, and creates no reports. It uses the core's source code through the
same Python interpreter. Review it before a live run. Then choose a provider and both
models explicitly, using currently supported model IDs from your provider:

```sh
~/finance-tools/tradingagents/bin/python scripts/run_tradingagents.py --workspace ~/my-private-finances --ticker AAPL --provider PROVIDER_ID --deep-model DEEP_MODEL_ID --quick-model QUICK_MODEL_ID --output ~/my-private-finances/research/aapl-first-run
```

Alternatively set `TRADINGAGENTS_LLM_PROVIDER`, `TRADINGAGENTS_DEEP_THINK_LLM`, and
`TRADINGAGENTS_QUICK_THINK_LLM` in the launching environment. The runner refuses missing
choices instead of selecting paid models. Provide the corresponding API credential via
your OS credential manager or process environment. Do not put keys in commands, chats,
this repository, or a tracked `.env`. Local providers still require an explicit model
choice; endpoint/provider configuration follows upstream documentation.

Live runs call upstream `PortfolioContext.model_validate(...)` and
`TradingAgentsGraph.propagate(..., portfolio=...)`. Current upstream sends portfolio
context to the trader, risk analysts, and portfolio manager. No vendored patch is needed.
[Upstream portfolio interface](https://github.com/TauricResearch/TradingAgents#current-holdings).

`--date` defaults to today in UTC, matching the core. The runner rejects historical dates
because it uses the current accepted ledger and cannot reconstruct past holdings. It
writes reports, model memory, and cache to a new external output directory. Provider and
data calls may incur charges, with no promised fixed cost or return. A research rating
is a proposal; this runner has no brokerage access or order execution.

## Use Vibe-Trading independently

After installation, run `~/finance-tools/vibe-trading/bin/vibe-trading --help`. Run its
configuration and research commands from your private workspace. Configure providers and
credentials there according to upstream instructions; installation alone does not grant
account access. This bundle does not automatically import Vibe-Trading output into the ledger.

Current upstream includes read-only portfolio sources, connector plugins, technical and
fundamental data tools, and research/backtesting workflows. It also contains live trading
capabilities, so select read-only profiles explicitly. Connector eligibility is not proof
that every asset or currency is supported: its portfolio documentation describes verification
levels and incomplete pricing/asset coverage. Use its OS-keyring onboarding where available.
[Vibe-Trading portfolio and connector documentation](https://github.com/HKUDS/Vibe-Trading#-local-multi-broker-portfolio).

## Account-source capability matrix

These upstream options require setup. This project does not include their adapters and
has not tested live account connections.
Save the source, account alias, observation time, currency, and coverage with each import.
Initial login and MFA remain with the account owner. Prefer official exports/APIs, then
use host-provided computer use to read a logged-in page when appropriate. A skill file
does not supply browser control, connector access, or authentication by itself.

| Source | Practical route | Boundary to verify |
|---|---|---|
| Robinhood | [Official Trading MCP](https://robinhood.com/us/en/support/articles/agentic-trading-overview/) | Reads linked accounts; trading is confined to a dedicated Agentic account. The overall server is not inherently read-only. Use a host-enforced read-tool allowlist or verified read-only adapter. Select the actual account returned by the broker. |
| IBKR | [Official MCP](https://www.interactivebrokers.com/en/trading/ai-integrations.php) for interactive review; [Flex Web Service](https://www.interactivebrokers.com/docs/web-api/flex-web-service/using-flex-web-service) for statements | MCP is `https://api.ibkr.com/v1/api/mcp-public`; AI instructions require user submission in IBKR. Current AI integration excludes India/Japan. Flex requires a configured query/token, generation then retrieval; its report date is not a live quote timestamp. |
| Coinbase | [Advanced Trade REST API](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api), with `view` permission only | Verify portfolio scope, all required balances and pagination. [Own-account API keys](https://docs.cdp.coinbase.com/coinbase-app/authentication-authorization/api-key-authentication) suit a local personal tool; applications accessing other users need OAuth. Do not enable `trade` or `transfer` for ledger gathering. |
| Coinbase MCP | [Official Coinbase MCP](https://docs.cdp.coinbase.com/ai-agents/coinbase-for-agents/coinbase-mcp) where the host is supported | Client allowlisting applies. Its setup guide targets trading/payments; do not adopt those permissions wholesale for this workflow. |
| Ethereum | [JSON-RPC `eth_getBalance`](https://ethereum.org/developers/docs/apis/json-rpc/) with a public address | Native ETH only; record the block and convert wei correctly. Token positions, staking, historical transactions, and tax basis need additional sources. Never request a wallet seed or signing key. |
| Other broker, bank, pension, stock plan, or private investment | Official export, statement, or authorized read through the host's computer-use tools | Reconcile all account sections and currencies; capture missing coverage as unknown. Require evidence for lots and basis. Separate holding balances from transactions to avoid double counting. |

## What the analysis can establish

Technical indicators need enough price history. A proposed IPO may have none: use issuer
filings, prospectus terms, capitalization/dilution, lockups, and valuation scenarios rather
than inventing technical signals. Keep investment research separate from tax conclusions.
This bundle can record sourced facts and draft scenarios; it does not file tax returns,
execute trades, transfer money, or establish audited investment performance. Save research
proposals separately from the user's confirmed decisions and actual transactions.
