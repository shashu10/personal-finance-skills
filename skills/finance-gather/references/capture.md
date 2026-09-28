# Capture and reconciliation

## API and exports

Read current official connector documentation before configuration. Distinguish a
read-only scope from a provider token that also permits transactions; this workflow
uses read operations only. Do not echo secrets, tokens, or credential-bearing URLs.
Keep raw evidence private, with the account alias and statement date in its filename.

Prefer structured export fields over OCR when available. Preserve original row IDs,
currency, sign, settlement/trade date semantics, fees, and statement balances. Inspect
headers and totals before mapping columns. A blank or unparsable amount is unknown.
Transfers between owned accounts are not income or investment return. Match both
sides where available and identify pending or missing counterparts.

## Computer use

Use the documented browser or desktop control tool exposed by the host. Open only
the institution and accounts covered by the user's request. If authentication is
needed, stop at the login challenge and let the user complete it in that interface.
Do not automate password entry or request recovery codes.

Observe account labels and page dates before extracting. Capture every relevant tab
and page: holdings, cash, margin/debt, account total, and lots if requested. Expand
pagination and distinguish current balances from order buying power. Prefer an
authorized download when it preserves more evidence than a visual transcription.
If only part of a table is accessible, record that coverage gap explicitly.

Save a concise capture note: account alias, source page/statement, displayed as-of
date, collection time, fields covered, visible totals, and extraction uncertainty.
Screenshots may contain identifiers; store only needed evidence in the private
workspace and exclude it from public artifacts. A hosted computer-use agent may
already send observed pages or screenshots to its model provider. Explain that data
flow when relevant; saving locally does not prevent it. Do not forward the evidence
to additional providers unless that sharing is authorized.

## Import contract

The input envelope is `{ "account": {...}, "transactions": [], "lots": [],
"fx_rates": {} }`; only `account` is required. One complete account snapshot per
import. Monetary amounts and quantities use decimal strings. Snapshot amounts and
quantities may be `null` when unknown; required transaction amounts and lot quantities
must be known before those records can be imported.

```json
{
  "account": {
    "id": "main-brokerage",
    "institution": "Example Brokerage",
    "type": "brokerage",
    "currency": "USD",
    "as_of": "2026-01-15",
    "source": "Private statement: evidence/main-brokerage-2026-01-15.pdf, page 2",
    "status": "verified",
    "include_in_totals": true,
    "restricted": false,
    "positions": [
      {"symbol": "EXAMPLE", "quantity": "10", "market_value": "1200.00", "cost_basis": null}
    ],
    "cash": "300.00",
    "liabilities": "0.00",
    "reported_total": "1500.00"
  }
}
```

This example is synthetic. Account types: `bank`, `brokerage`, `retirement`, `hsa`,
`pension`, `education`, `crypto`, `other`. Status: `verified`, `estimated`, `unverified`.
Verification means source-backed and reconciled, not merely successfully parsed.
Cash and liabilities are nonnegative; represent an overdraft as a liability. The
current core supports long-only positions. Do not encode a short as a long or silently
drop it: preserve unsupported positions in evidence and report incomplete coverage.

`reported_total` is net: positions + cash - liabilities, in the account currency.
The complete figures must reconcile within 0.01 native currency units. Do not
substitute buying power for cash, net equity for gross holdings, or unrealized gain
for market value. Set `include_in_totals: false` on overlapping wrapper accounts.
Preserve restricted status; restricted value is not automatically spendable cash.

An FX item is `"EUR": {"rate":"1.10","as_of":"2026-01-15","source":"source citation"}`:
one EUR equals 1.10 units of the ledger's base currency. Use a dated source and do
not apply current FX to historical tax basis without a stated jurisdictional method.

Transactions require `id`, `account_id`, `date`, `type`, `amount`, `currency`.
Types include `transfer`, `income`, `expense`, `buy`, `sell`, `dividend`, `fee`, `other`.
Lots require `id`, `account_id`, `symbol`, `acquired_on`, `quantity`, `cost_basis`,
`currency`. Preserve native signs and dates according to the installed contract.
Transaction amounts are signed decimal strings, lot quantities are positive decimal
strings, and lot cost basis may be `null`. Preserve incomplete transaction or lot
rows as private evidence with a coverage note until the required fields are known.
Use provider IDs prefixed by stable account alias, or a deterministic hash of source
identity and row content; never use collection time as a deduplication key.

When sources disagree, compare dates, settlement, currency, pending transactions,
corporate actions, and account scope. Keep unresolved items visible. An estimated
private-company mark remains estimated even when accurately transcribed.
