# Memory records

The workspace uses `facts.json` and `decisions.json`, each with
`{"schema_version":1,"items":[]}`. Use `finance-core memory --input FILE` to merge
an envelope containing one or both lists. All dates below are synthetic examples.

## Confirmed fact

```json
{
  "facts": [
    {
      "id": "housing-budget-2026-01-15",
      "date": "2026-01-15",
      "text": "User confirms monthly housing expense of 1800 EUR, excluding utilities, effective February.",
      "source": "User statement in planning conversation on 2026-01-15",
      "user_confirmed": true
    }
  ]
}
```

Required fact fields: `id`, `date`, `text`, `source`, `user_confirmed: true`.
Text should preserve currency, frequency, effective date, and scope when relevant.
If an estimate is explicitly the user's estimate, say so; do not make it a verified
account balance. Sensitive facts need only the detail required for future usefulness.

## Proposal and accepted decision

```json
{
  "decisions": [
    {
      "id": "cash-reserve-proposal-2026-01-15",
      "date": "2026-01-15",
      "status": "proposal",
      "text": "Consider a dedicated cash reserve after reviewing essential expenses.",
      "source": "Private report: reports/cash-plan-2026-01-15.md",
      "user_confirmed": false
    },
    {
      "id": "cash-reserve-choice-2026-01-16",
      "date": "2026-01-16",
      "status": "confirmed",
      "text": "User chooses to retain 12000 EUR as a cash reserve; no account transfer has occurred.",
      "source": "User acceptance in conversation on 2026-01-16",
      "user_confirmed": true,
      "supersedes": "cash-reserve-proposal-2026-01-15"
    }
  ]
}
```

Required decision fields: `id`, `date`, `status`, `text`, `source`, `user_confirmed`.
Allowed statuses are `proposal`, `confirmed`, `executed`. The latter two require true
confirmation. An executed record should say whether evidence is an imported fill,
statement, receipt, or a user's completion report. It does not mutate `ledger.json`.
If recording a rejection, use a confirmed decision whose text states the rejected
proposal and conditions; do not invent an unsupported `rejected` status.

## Supersession and retrieval

Use a new stable ID plus `supersedes` to correct or replace a record. The target must
exist in the same record collection at an earlier or equal date. Keep the old record;
never edit its text to make history look consistent. Avoid cycles or ambiguous
branches. For the current view, follow supersession to the latest applicable record
and check its effective conditions. The core stores history; the agent interprets
which facts apply to the current question.

A new address, job, or filing year does not retroactively change the past. Record
when it became true. A legal conclusion belongs in a dated research report; if the
user reports a professional opinion, preserve exactly that attributed statement.

Before saving, compare the proposed envelope with existing entries. After saving,
verify the actual records and disclose any unresolved contradiction. The CLI can
validate structure and confirmation flags but cannot certify the truth of a statement.
