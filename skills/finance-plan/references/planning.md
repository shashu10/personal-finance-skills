# Planning methods

## Inputs and cash flow

Use net spendable income and expenses on the same monthly, base-currency basis.
Distinguish salary, variable compensation, benefits, vesting, investment distributions,
and asset-sale proceeds. Unvested equity and hoped-for employment are not current cash.
Transfers between owned accounts do not create income. A borrowing inflow is debt.

Build an expense breakdown from actual or confirmed spending:

| Component | Treatment |
| --- | --- |
| Essential recurring expenses | Monthly amount, currency, source and date |
| Discretionary expenses | Separate reduction scenario if the user wants it |
| Irregular annual costs | Allocate over months or schedule explicitly, stating which |
| Debt minimums and interest | Include once; identify variable rates and due dates |
| One-time goals/costs | Date and funding source; avoid including again in monthly burn |
| Tax reserves | Sourced estimate or explicit unknown, separate from net income assumptions |

The core stores transactions but does not infer a budget from them. If deriving
spending, classify the requested date range, remove internal transfers and duplicated
imports, distinguish refunds, and reconcile with statement totals. State when you
extrapolate from an incomplete period. Preserve the calculation as a private artifact.

## Core runway versus extended scenarios

`finance-core plan` uses eligible unrestricted cash only and explicit monthly
income/expenses and one-time costs. It does not assume any security sale or investment
return. If monthly net spending is zero or negative, explain that cash is not depleted
under the stated assumptions rather than promising perpetual financial security.

For extensions, show an input table and deterministic arithmetic separately:

- Asset sale: sale value, fees, estimated tax, settlement timing, and remaining exposure.
- Debt payoff: amount, rate, fee/promo terms, payment date, and remaining emergency cash.
- Job change: income start/stop dates, benefits changes, variable compensation and tax timing.
- Home or family goal: upfront cost, continuing cost, contingencies, and unavailable funds.
- Portfolio drawdown: affected assets and timing; cash and liabilities do not all move together.

Do not give every dollar of gross assets the same liquidity or return assumption.
For private holdings, distinguish cost, estimated mark, and realizable proceeds.
For retirement or healthcare accounts, separately establish permitted uses and
withdrawal consequences before considering them as a funding source.

## Scenario output

Name cases by the actual assumption, such as "income starts three months later."
Show the changed inputs, outcome, and unresolved dependencies. Avoid deterministic
claims about market appreciation. Expected returns are neither cash flow nor guarantees.
If taxes or expenses are uncertain, show a sensitivity range instead of a single
precise outcome. State each model limitation beside the affected result.

Record accepted decisions with date, source, condition and review trigger. Save
rejected alternatives as rejected in descriptive text when useful, without pretending
they were executed. A later plan should respect the latest confirmed decision.
