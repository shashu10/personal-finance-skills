# Synthetic examples

These fixtures describe an invented household. They contain no personal data or real
security recommendations. Dates are fixed deliberately so repeated runs are reproducible.
Use the matching `--as-of 2026-01-20` for assessments; using today's date correctly reports
these snapshots as stale. For a fresh runnable demonstration, `init --demo` creates
synthetic snapshots dated today instead.

After installing the package, run from the repository root:

```sh
finance-core init --workspace ~/.local/share/finance-example
finance-core import --workspace ~/.local/share/finance-example --input examples/account-import.json
finance-core import --workspace ~/.local/share/finance-example --input examples/account-import.json
finance-core summary --workspace ~/.local/share/finance-example --as-of 2026-01-20
finance-core plan --workspace ~/.local/share/finance-example --monthly-expenses 500 --as-of 2026-01-20
finance-core review --workspace ~/.local/share/finance-example --proposal examples/trade-proposal.json --as-of 2026-01-20
finance-core memory --workspace ~/.local/share/finance-example --input examples/memory.json
```

The second import adds no duplicate transactions or lots. With the default unset risk
limits, the review returns `report_only`. It does not claim the proposed trade is suitable
or place an order. Keep demo and real data in separate workspaces.

The JSON schemas describe shapes for editors and adapter authors. The Python validator
also applies semantic checks that JSON Schema cannot express: reconciliation, chronology,
positive quantities, numeric limits, unique IDs, account references, and confirmation
history. Always run `finance-core validate` after importing or editing private data.
