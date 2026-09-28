# Private workspace contract

All JSON uses `schema_version: 1`. Amounts and quantities are finite decimal strings.
Use `null` for unknown amounts; never substitute zero. Dates are ISO calendar dates.
Currency codes are three uppercase letters. Amounts in accounts, transactions, lots,
and trade proposals are in their stated native currency. `fx_rates` express one unit
of foreign currency in the ledger's base currency and carry their own date and source.

Run `finance-core init --workspace /private/path --base-currency USD`. Without
`--workspace`, use `FINANCE_WORKSPACE`, otherwise `~/.local/share/personal-finance-skills`.
Every command accepts `--workspace`. Data paths inside this public checkout are refused,
including paths whose symlinks resolve inside it. Existing data files cannot be symlinks.
Initialization is idempotent and never overwrites existing files. Demo data requires
`--demo`; missing real data never falls back to a demo.

## Files

- `ledger.json`: `base_currency`, `accounts`, and `fx_rates`.
- `transactions.json`: append-only `items`, deduplicated by stable `id`.
- `lots.json`: `items`, deduplicated by stable `id`.
- `facts.json`: `items` of explicitly user-confirmed statements with provenance.
- `rules.json`: `max_age_days` (7 initially), nullable concentration and debt limits,
  and explicit model-sharing switches (both initially false).
- `decisions.json`: `items` distinguishing `proposal`, `confirmed`, and `executed`.

Private directories use mode 0700 and written files use mode 0600 on POSIX systems;
existing workspaces with group or other access are refused rather than silently having
their permissions changed. Windows users should use a private user directory with
appropriate Windows ACLs. The importer validates
the complete prospective state before preparing replacement files, then replaces files
atomically and rolls back ordinary write errors. This is not a database transaction:
an operating-system crash during multiple replacements may require re-import/reconciliation.
Keep private backups. Concurrent commands serialize through a workspace lock.

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
children. This is an explicit importer responsibility; the core cannot discover hidden
overlap. Missing, unverified, estimated, stale, and future-dated included data prevent a
summary from being considered ready for planning or proposal assessment.

Transactions require `id`, `account_id`, `date`, `type`, `amount`, `currency`;
types include `transfer`, `income`, `expense`, `buy`, `sell`, `dividend`, `fee`, and
`other`. Transfer amounts are not treated as income. The core does not automatically
derive income or expenses from transactions. Lots require `id`, `account_id`, `symbol`,
`acquired_on`, `quantity`, `cost_basis`, and `currency`. Identical IDs are idempotent;
conflicting contents are rejected. IDs are globally unique within their file. Older
account snapshots are rejected. Same-date corrected snapshots are accepted only through
an explicit `--replace-same-date` import flag. A repeated identical snapshot is a no-op.

## Planning, proposals, and sharing

`summary --as-of YYYY-MM-DD` reports base-currency totals and explains unknown/stale
inputs. `plan` requires explicit monthly expenses; income and one-time cost default to
zero. It uses unrestricted included cash in non-retirement accounts only. It does not
assume securities can be sold, include retirement/HSA balances, estimate taxes, or
schedule debt repayments. Current debt remains visible in the balance-sheet summary.

`review --proposal FILE` accepts `account_id`, `symbol`, `side` (`buy` or `sell`),
`quantity`, `price`, and `as_of`. It computes a hypothetical cash-funded transaction,
post-trade symbol concentration and debt/assets. Quantities must be positive and sells
cannot exceed recorded holdings. Buys cannot exceed recorded cash. Explicit prices are
used as scenario inputs; the core does not fetch quotes. Existing holdings are adjusted
at their recorded average marked value, with execution-price differences changing the
projected account net value. Fees and taxes are not modeled. Null limits mean report
only. Missing, unknown, stale, future-dated, or unverified inputs produce `needs_data`,
never `within_limits`. No command places orders.

`context --ticker SYMBOL --format relative` requires `sharing.relative_context: true`.
It emits selected ticker exposure and fractions, without account identifiers or balances.
`--format tradingagents` additionally requires `sharing.tradingagents_amounts: true`
and emits upstream's `{cash,currency,positions:[{ticker,quantity,average_price?}]}` payload.
This exports all included positive holdings, because upstream
needs existing holdings rather than treating unmentioned positions as absent. Known cost
bases for positions denominated entirely in base currency are divided by quantities;
unknown or foreign-currency cost bases omit `average_price`. `cash` is `null`: household
cash is not necessarily deployable at the selected broker. The arithmetic remains Decimal internally; this upstream payload alone
uses JSON numbers required by its interface. Incomplete or stale data returns exit code 2.
No upstream invocation is made. These flags authorize export generation, not arbitrary model transmission.

`memory --input FILE` accepts `decisions` and/or `facts` lists. Decisions require `id`,
`date`, `status`, `text`, `source`, and `user_confirmed`; `confirmed` and `executed`
statuses require `user_confirmed: true`. Facts require `id`, `date`, `text`, `source`,
and `user_confirmed: true`. This command records user confirmation supplied by the caller;
it cannot independently prove consent or a trade execution. Proposals remain proposals.
Repeated identical entries are ignored and conflicting IDs are rejected.
