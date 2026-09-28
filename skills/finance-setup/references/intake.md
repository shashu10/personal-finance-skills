# Gradual intake and confirmed facts

Ask in small groups tied to the user's question. Prefer a short answer or choices
when possible, and preserve any earlier explicit answers.

| Topic | Useful facts | Do not infer |
| --- | --- | --- |
| Coverage | Institutions, account types, ownership, currencies, liabilities, statement dates | That an omitted account has zero value |
| Work and income | Employment status, reliable net income, income currency, bonus variability, benefits, equity vesting | Future employment, guaranteed bonuses, or access to unvested shares |
| Spending | Essential and discretionary monthly spending, irregular annual costs, minimum debt payments | Spending from withdrawal totals or transfers alone |
| Household | Dependents, shared expenses, ownership and intended scope | Marital status or a partner's financial consent |
| Goals | Amount, date, priority, liquidity needs and acceptable uncertainty | A risk limit from age, wealth, or profession |
| Tax | Relevant year, jurisdictions, actual presence dates, citizenship/residence permits, filing status, sourced professional advice | Tax residence or a universal rate from nationality or a planned move |

Collect legal names, full addresses, birth dates, identification numbers, and partner
details only when the immediate task actually needs them. An alias usually suffices.

Save observed statements separately from conclusions. For example, a confirmed
departure date is a fact; the effect on tax residence is a dated research conclusion
with its own assumptions. An assistant estimate is not a confirmed personal fact.

Use an actual ISO date and a source such as a user statement reference or private
document path. Amounts belong in text with currency and frequency to avoid ambiguity.
An illustrative memory envelope is:

```json
{
  "facts": [
    {
      "id": "income-confirmed-2026-01-15",
      "date": "2026-01-15",
      "text": "User reports expected monthly take-home income of 4200 EUR starting February; bonus excluded.",
      "source": "User statement in setup conversation on 2026-01-15",
      "user_confirmed": true
    }
  ]
}
```

The sample is synthetic. Use stable IDs for actual records and new IDs for changes.
To correct an earlier statement, add `supersedes` with the earlier ID and explain
the effective date. Preserve the old record and never promote a guess to confirmed.

A useful private intake note has three short sections: confirmed statements,
unanswered questions relevant to the current task, and account coverage. Keep it
outside the source checkout. Saving a fact does not mean sharing it with an API.
