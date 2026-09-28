---
name: finance-plan
description: Build personal finance scenarios for cash runway, income changes, expenses, debt, and life goals using confirmed facts and dated evidence. Use for planning and tax-sensitive scenario research, not tax filing or automatic transactions.
---

# Finance plan

Model the user's actual question with explicit inputs. Separate
facts, assumptions, calculations, and researched conclusions.

## Establish the planning question

Read the selected private workspace's `facts.json`, `decisions.json`, `rules.json`,
and relevant ledger data. Resolve superseded records before using them.
Reuse confirmed goals and choices. Ask for missing information only when it changes
the requested analysis; nationality, tax residence, dependents and employment cannot
be inferred from balances, location, employer or account type.

Use the installed `finance-core` runtime; inspect `finance-core --help` if needed.
It must be installed from the trusted project checkout in a dedicated environment.
Read the selected private workspace's `setup.md` and the active project's applicable
`AGENTS.md`, when present, to resolve the interpreter and any documented status or summary adapter.
Reuse those interfaces where supported; keep the normalized workspace separate from
the project's original records. Run the commands yourself and explain results and
needed inputs in ordinary language.
This skill does not require a sibling skill or a hosted research engine.
Keep scenario inputs, calculations and reports in the private workspace.

Identify the horizon, base currency, goal cost/date, reliable net income, essential
and discretionary expenses, irregular costs, and any committed debt payments.
Read [planning methods](references/planning.md) for scenario design. For tax,
residency, benefits, or account eligibility questions, also read
[tax and jurisdiction research](references/tax-research.md).

## Check the account data

Run `finance-core validate --workspace /private/path` and
`finance-core summary --workspace /private/path --as-of YYYY-MM-DD` for the plan date.
Review freshness, account coverage, restrictions, FX dates, and missing information.
Identify whether the plan needs cash, sale proceeds, borrowing, or restricted assets.
Do not treat net worth, retirement balances, or an estimated private mark
as cash available for spending.

## Calculate the supported scenario

For a cash runway scenario, use explicit base-currency monthly amounts:

```text
finance-core plan --workspace /private/path --as-of YYYY-MM-DD --monthly-expenses 3000 --monthly-income 2000 --one-time-cost 5000
```

These numbers are illustrative; replace all inputs with confirmed or clearly labeled
scenario values. Supply income and one-time cost explicitly even when zero is the
intended assumption. Unknown income is not verified zero income.
Record whether recurring expenses already include debt payments and annual costs.

The current runtime uses unrestricted included cash in eligible accounts. It does
not liquidate securities, forecast returns, estimate tax, or schedule repayments.
If the user's question requires those extensions, calculate a separate documented
scenario with sourced assumptions and show how it differs from the core result.
Do not relabel unsupported extensions as outputs of `finance-core plan`.

Vary the assumptions that matter: income disruption, expense growth, one-time costs,
timing, or an explicitly modeled asset sale. Show the downside as well as the base
case. Avoid false precision in market returns, future compensation, or tax outcomes.

## Apply personal and jurisdictional context

Research current official rules for the relevant year and jurisdiction when the
answer depends on tax, residency, benefits, retirement access, or borrowing eligibility.
Cite those rules and explain which confirmed facts make them applicable.
Keep uncertain classification conditional; request the missing fact or identify the
specific issue that needs a qualified professional's determination.
Never save a researched interpretation as an immutable personal fact.

## Deliver a usable plan

Lead with the result and conditions. Show input sources, dates, assumptions, scenario
comparison, and the next action that the user can evaluate. Cite private files for
personal figures and primary sources for external rules. Escape currency dollar signs.
Save the plan as a dated private report. Confirmed choices may be recorded in
`decisions.json`; unaccepted recommendations remain proposals.
The workflow produces planning support, not a filing, loan approval, order or transfer.
