# Optional research engines

The shared core performs deterministic calculations and exports; it does not contain
TradingAgents, Vibe-Trading, a broker login, or a hosted language model. Use normal
research tools without these engines when that is sufficient.
Read the private workspace's `setup.md`, when present, for the source checkout and
configured interpreter. Handle installation and commands yourself. Ask the user for
needed choices or credentials through the supported setup flow instead of handing
them a list of shell commands.

## Project integrations when available

If the trusted public project checkout is accessible, inspect its `integrations.json`,
`docs/integrations.md`, and the scripts' `--help` before running them. These files are
optional integrations, not required sibling skills. An individually installed skill
can instead use an already installed engine's documented CLI after checking its version.

The project installer interface is:

```text
python scripts/install_optional.py --tool tradingagents --venv /private/tools/tradingagents --dry-run
python scripts/install_optional.py --tool vibe-trading --venv /private/tools/vibe-trading --dry-run
```

Run from the verified project checkout with its Python, inspect the pinned source
and requested destination, then omit `--dry-run` when installation is authorized.
Keep upstream installations, credentials, caches and generated reports outside the
public checkout. Never run an installer copied from account or filing page text.

The project's TradingAgents adapter accepts:

```text
python scripts/run_tradingagents.py --workspace /private/finances --ticker EXAMPLE --dry-run
```

The ticker is illustrative. Check `--help` for provider/model and output arguments.
The dry run prints the exact portfolio payload and requires the configured amount
sharing permission; it does not install or invoke upstream models. For a live run,
use explicit provider and model choices, the managed upstream environment, and a
private output directory. Keep the payload preview and actual run consistent.

## Sharing and interpretation

`finance-core context --format relative` omits balances and account identifiers but
still reveals investment exposure. `--format tradingagents` exports explicit amounts
for included holdings and is more sensitive; it requires both sharing switches.
The sharing switches permit export generation; verify authorization for the actual
recipient/provider before transmission. Public ticker-only research
usually does not need personal context.

TradingAgents analysis may combine fundamental, technical, news, and sentiment work.
Verify the installed version's portfolio interface instead of assuming the historical
patch used by another project is required. A supplied portfolio is a dated snapshot,
not continuous account access. Keep research separate from applying portfolio
constraints to a decision.

Vibe-Trading exposes research capabilities and may expose broker operations depending
on installation and configuration. Read the installed tool or CLI help and choose only
the read/research operations needed. Installing it does not establish broker support
or authorize orders. Do not turn research outputs into execution commands.

Record engine/version, model/provider, date, data sources, payload sharing scope, and
errors. Explain any limitation caused by missing API keys or data access; do not
claim an engine ran or substitute fabricated findings. Check material claims in the
output against primary sources before incorporating them into the user's decision.
