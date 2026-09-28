# Optional research engines

The shared core performs deterministic calculations and exports; it does not contain
TradingAgents, Vibe-Trading, a broker login, or a hosted language model. Use normal
research tools without these engines when that is sufficient.
Read the selected private workspace's `setup.md` and the active project's applicable
`AGENTS.md`, when present, for the configured interpreter and research adapters.
Handle installation and commands yourself. Ask the user for needed choices or
credentials through the supported setup flow instead of handing
them a list of shell commands.

## Existing private project adapters

Prefer a documented project adapter when it supplies the context, policy checks, and
report locations required by this user's workflow. Inspect its configuration and help
before running it. Some projects provide a command like:

```text
python scripts/run_skill_research.py EXAMPLE --mode technical --dry-run
python scripts/run_skill_research.py EXAMPLE --mode fundamental --dry-run
python scripts/run_skill_research.py EXAMPLE --mode both --dry-run
```

These illustrative commands run from the selected private project with its recorded
interpreter. The public skills bundle does not supply this host-project script.
A project may map `technical` to TradingAgents and `fundamental` to Vibe-Trading;
inspect the actual mapping instead of inferring it from an installed package name.

Check the dry-run result for the requested ticker, mode, model/provider, sharing scope,
and output paths. Use a live run only within the user's existing authorization for
the research and model calls. Preserve the workspace's export permissions and the
project's existing portfolio-context and risk checks. A successful dry run is not a
completed analysis, and a generated report is not an account refresh or an executed trade.

Keep recurring work tied to the user's requested schedule. A daily review can read
existing dated reports or run the configured research adapter when authorized; skill
installation alone does not schedule paid model calls. If the adapter is absent, use
the portable integration below or public-source research as appropriate to the task.

## Portable optional integrations

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
