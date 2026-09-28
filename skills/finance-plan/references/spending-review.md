# Spending and budget review

Start with the requested period and question: where money went, what changed, whether
a budget held, or how much a planned purchase would leave. Read the relevant account
exports and existing decisions. Collect additional records only where a gap could
change the answer. Keep raw evidence intact.

The core stores normalized transactions; it does not categorize spending, match
transfers, or calculate a monthly budget. Use the agent's available code tools for
the analysis and save the calculation and classifications privately. Do not invent
a `finance-core budget` command or describe those calculations as core output.

## Establish coverage

Record each source's account alias, currency, date range, pending/posted status, and
whether all pages were captured. Use one stated date convention, normally posting
date. Keep pending activity separate until it settles. Compare like periods: an
incomplete month cannot establish a full-month decline in spending.

Deduplicate by stable source IDs before aggregating. A matching amount and date alone
do not prove duplication. Preserve a private classification table with source row/ID,
original description, amount, currency, assigned treatment, and any uncertainty.
Unclear merchants stay unclassified unless other evidence resolves them.

## Treat the transactions correctly

| Item | Treatment |
| --- | --- |
| Transfer between owned accounts | Match both sides where possible and exclude from household income/spending. Keep unmatched candidates unresolved. |
| Credit-card purchases and payment | Count posted purchases, refunds, interest and fees in spending. Exclude the card repayment from consumption when those purchases are included. A checking-only export shows the repayment cash outflow but cannot reveal its spending categories. |
| Refund or reimbursement | Link it to the original expense when supported. Show gross purchases and credits separately before net spending. Explain a refund crossing the review boundary instead of inventing a current-period purchase. |
| Debt principal, borrowing, investment purchase or sale | Separate financing and asset movements from consumption and earned income. Include actual debt service in a cash requirement view without counting principal twice. |
| Cash withdrawal | Track the cash movement. Its purpose remains unknown until supported by cash-expense records. |
| Shared expense | Apply a documented household scope and confirmed reimbursement/share; do not assume the full amount belongs to the user. |
| Irregular annual cost | Show actual payment in the observed period. If smoothing it for a future budget, label the monthly allocation and avoid adding the annual payment again. |

Keep a consumption view and a cash movement view distinct when card repayments,
debt service, or asset sales make them differ. State which view the result answers.
Never infer take-home income from every credit to a bank account.

Preserve native amounts. Combine currencies only with a cited conversion method and
dated rates appropriate to the analysis. A statement's converted settlement amount
can be used when recorded. Without FX evidence, report separate currency subtotals;
do not reuse today's ledger FX silently for historical spending.

Reconcile classifications with the source totals for the same posted date range.
Explain exclusions, credits, and unresolved rows. When opening/closing balances are
available, reconcile all account movements separately from the spending subtotal.
Leave a mismatch visible instead of inserting an unexplained balancing expense.

## Compare and save

Use the user's existing categories and budget if available. Suggested categories,
savings targets, and spending cuts remain proposals. Avoid assigning a universal
budget ratio or changing a confirmed target without the user.

For recurring expenses, compare observed merchant, dates, frequency and amounts.
Label a possible subscription or price increase as a candidate until evidence supports
it. One charge does not establish a monthly commitment. Reviewing a subscription does
not authorize cancelling it.

Save a dated report with the coverage, main finding, calculation file and source links.
Use this compact table where it answers the question; remove unused columns. Define
variance as actual net spending minus budget, so a positive amount means over budget.

| Category | Actual net spending | Confirmed budget | Variance | Source and coverage |
| --- | --- | --- | --- | --- |
| Observed category | Amount and currency | Amount or unknown | Amount or unknown | Statement/row IDs, dates, unresolved items |
| Unclassified | Amount and currency | Unknown | Unknown | Rows requiring review |

For a month-to-month comparison, substitute the prior comparable period for budget
and explain the largest supported changes. Show unknowns and missing accounts beside
the result. End with the useful next step, such as resolving an unmatched transfer or
checking a repeated fee. Save any accepted budget change through the memory workflow;
an analysis alone does not confirm a new plan.
