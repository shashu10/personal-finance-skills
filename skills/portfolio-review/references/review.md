# Review semantics and proposals

Use `finance-core summary` and `review` outputs for calculations rather than mental
arithmetic. Keep manual extensions clearly separate from what the core computed.

## What the runtime measures

- Account values use their native currencies; the runtime converts them to the base currency using dated FX.
- Gross assets are included position values plus cash. Liabilities are separate.
- Net worth is gross assets less liabilities; this is not spendable cash.
- An excluded wrapper account contributes no additional assets or debt to totals.
- Restriction and account type affect cash eligibility for runway calculations.
- Symbol concentration uses included assets; exact symbols are not a full economic
  exposure model. Different listings and fund holdings require an explicit mapping.

The runtime does not discover missing accounts or inspect the underlying statements.
Read coverage notes and validate the inventory before claiming a complete picture.
Resolve stale, future-dated, or unknown source and FX data instead of weakening freshness rules
just to obtain a favorable status. User choices of freshness policy remain theirs.

`rules.json` initially has these limits:

```json
{
  "max_position_fraction": null,
  "max_debt_to_assets": null
}
```

Values are fractions, not whole-number percentages. For example, an explicitly
user-chosen 20 percent ceiling is `"0.20"`. This is an illustrative conversion,
not a recommended threshold. Do not add a default tolerance or risk appetite.

## Hypothetical proposal

```json
{
  "account_id": "main-brokerage",
  "symbol": "EXAMPLE",
  "side": "buy",
  "quantity": "2",
  "price": "100.00",
  "as_of": "2026-01-15",
  "confirmed": false
}
```

This is synthetic. Use an existing account alias, a positive quantity, native-currency
price, and the actual proposal date. `confirmed` is descriptive; it is not authority
to execute a trade. The CLI checks recorded cash for buys and holdings for sells.
Borrowing, short positions, derivatives, contingent orders and lot-specific taxes
are outside this initial proposal model.

The core reduces or increases existing holdings at their recorded average marked value;
the execution-price difference affects projected net value. A proposed limit price
is not a fresh mark for the entire portfolio. State the price's source and whether
it is a quote, user scenario, or assumed execution. The core does not fetch quotes.

The report can flag a user-limit breach or insufficient data. It cannot prevent an
order at a broker. Passing configured limits is not a prediction or a complete
suitability assessment; taxes, fees, liquidity, ownership, and the user's goals may
still change the conclusion.

When saving a decision, keep `proposal`, `confirmed`, and `executed` distinct. An
actual fill has a date, price, quantity and evidence; a requested trade does not.
