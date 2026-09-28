# Private workspace contract

All JSON uses `schema_version: 1`. Amounts and quantities are finite decimal strings.
Use `null` for unknown amounts; never substitute zero. Dates are ISO calendar dates.
Currency codes are three uppercase letters. Amounts in accounts, transactions, lots,
and trade proposals are in their stated native currency. `fx_rates` express one unit
of foreign currency in the ledger's base currency and carry their own date and source.

Run `finance-core init --workspace /private/path --base-currency USD`. Without
`--workspace`, use `FINANCE_WORKSPACE`, otherwise `~/.local/share/personal-finance-skills`.
Every command accepts `--workspace`. The core rejects data paths inside this public
checkout, including paths whose symlinks resolve inside it. Existing data files cannot
be symlinks. You can repeat initialization without overwriting existing files. Demo
data requires `--demo`; the core never substitutes demo data for missing real data.

## Files

- `ledger.json`: `base_currency`, `accounts`, and `fx_rates`.
- `transactions.json`: append-only `items`, deduplicated by stable `id`.
- `lots.json`: `items`, deduplicated by stable `id`.
- `facts.json`: `items` of explicitly user-confirmed statements with provenance.
- `rules.json`: `max_age_days` (7 initially), nullable concentration and debt limits,
  and explicit model-sharing switches (both initially false).
- `decisions.json`: `items` distinguishing `proposal`, `confirmed`, and `executed`.

The core creates private directories with mode 0700 and writes files with mode 0600 on
POSIX systems. It rejects existing workspaces that allow group or other access without
changing their permissions. On Windows, use a private user directory with appropriate
Windows ACLs. The importer validates the complete resulting workspace before preparing
replacement files, then replaces each file atomically and rolls back ordinary write
errors. These replacements do not form a database transaction. An operating-system
crash during multiple replacements may require re-importing and reconciling the data.
Keep private backups. A workspace lock serializes concurrent commands.

## Accounts and imports

An import is an object containing `account` (a complete snapshot), with optional
`transactions`, `lots`, and `fx_rates`. Required account fields are `id`, `institution`,
`type`, `currency`, `as_of`, `source`, `status`, `include_in_totals`, `restricted`,
`positions`, `cash`, and `liabilities`. Use an alias such as `main-brokerage` for `id`.
`status` is `verified`, `estimated`, or `unverified`. Supported account types are
`bank`, `brokerage`, `retirement`, `hsa`, `pension`, `education`, `crypto`, and `other`.
`reported_total`, when supplied, is net account value: cash plus positions minus
liabilities. Complete figures must reconcile within 0.01 native currency units.

Positions contain `symbol`, `quantity`, `market_value`, and optional `cost_basis`.
All position values are nonnegative; long-only positions are supported in this release.
Cash and liabilities are nonnegative or unknown. Record a cash overdraft as a liability.
Set `include_in_totals: false` on any parent/wrapper account already represented by its
children. Whoever prepares the import must identify these overlaps; the core cannot
discover them. A summary is not ready for planning or proposal assessment if included
data is missing, unverified, estimated, stale, or future-dated.

Transactions require `id`, `account_id`, `date`, `type`, `amount`, `currency`;
types include `transfer`, `income`, `expense`, `buy`, `sell`, `dividend`, `fee`, and
`other`. Transfer amounts are not treated as income. The core does not automatically
derive income or expenses from transactions. Lots require `id`, `account_id`, `symbol`,
`acquired_on`, `quantity`, `cost_basis`, and `currency`. Repeating an ID with identical
contents makes no change; the core rejects conflicting contents. IDs are globally
unique within their file. The core rejects older account snapshots and accepts corrected
snapshots for the same date only with the explicit `--replace-same-date` import flag.
A repeated identical snapshot makes no change.

## Planning, proposals, and sharing

`summary --as-of YYYY-MM-DD` reports base-currency totals and explains unknown/stale
inputs. `plan` requires explicit monthly expenses; income and one-time cost default to
zero. It uses unrestricted included cash in non-retirement accounts only. It does not
assume securities can be sold, include retirement/HSA balances, estimate taxes, or
schedule debt repayments. Current debt remains visible in the balance-sheet summary.

`review --proposal FILE` accepts `account_id`, `symbol`, `side` (`buy` or `sell`),
`quantity`, `price`, and `as_of`. It computes a hypothetical cash-funded transaction,
post-trade symbol concentration and debt/assets. Quantities must be positive and sells
cannot exceed recorded holdings. Buys cannot exceed recorded cash. The core uses the
supplied prices for the scenario and does not fetch quotes. It adjusts existing holdings
at their recorded average marked value; differences from the execution price change
the projected account net value. The calculation excludes fees and taxes. Null limits
mean report only. Missing, unknown, stale, future-dated, or unverified inputs produce `needs_data`,
never `within_limits`. No command places orders.

`context --ticker SYMBOL --format relative` requires `sharing.relative_context: true`.
It emits selected ticker exposure and fractions, without account identifiers or balances.
`--format tradingagents` additionally requires `sharing.tradingagents_amounts: true`
and emits upstream's `{cash,currency,positions:[{ticker,quantity,average_price?}]}` payload.
The exporter sends every included positive holding so upstream does not treat omitted
positions as absent. For positions denominated entirely in base currency, the exporter
divides known cost bases by quantities. It omits `average_price` for unknown or
foreign-currency cost bases. It sets `cash` to `null` because household cash may not be
available at the selected broker. The core uses Decimal arithmetic internally; only
this upstream payload uses JSON numbers, as its interface requires. Incomplete or stale
data returns exit code 2. The exporter does not run upstream. These flags permit export
generation only; sending data to a model requires separate authorization.

`memory --input FILE` accepts `decisions` and/or `facts` lists. Decisions require `id`,
`date`, `status`, `text`, `source`, and `user_confirmed`; `confirmed` and `executed`
statuses require `user_confirmed: true`. Facts require `id`, `date`, `text`, `source`,
and `user_confirmed: true`. This command records user confirmation supplied by the caller;
it cannot independently prove consent or a trade execution. Proposals remain proposals.
The core ignores repeated identical entries and rejects conflicting IDs.
