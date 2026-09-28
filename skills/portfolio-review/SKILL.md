---
name: portfolio-review
description: Review a sourced personal balance sheet, cross-account exposure, and hypothetical trades against the user's explicit limits. Use for portfolio checkups and proposal assessment, not order execution.
---

# Portfolio review

Explain the portfolio's condition and the effect of a proposed change using verified
inputs. A stock's research rating and suitability for this portfolio are separate questions.

## Load the current state

Use the installed `finance-core`; inspect `finance-core --help` if needed. The runtime
must be installed from the trusted project checkout in a dedicated environment.
Read the private workspace's `setup.md` to resolve the configured interpreter. Run
the commands yourself; explain results and needed inputs in ordinary language.
Read `ledger.json`, `rules.json`, `facts.json`, and `decisions.json` in the selected
private workspace. Resolve superseded records and distinguish confirmed decisions
from earlier model suggestions. This skill is usable without sibling skills.

Run `finance-core validate --workspace /private/path`, then
`finance-core summary --workspace /private/path --as-of YYYY-MM-DD` using the review date.
Review source dates, currency/FX dates, included accounts, restricted assets, and
known coverage gaps. Confirm that wrapper accounts are not counted twice.
Missing, stale, unverified, estimated, or future-dated data cannot support a definitive
within-limits finding. A successful schema check does not establish complete coverage.

## Explain the balance sheet

Read [review semantics](references/review.md) before interpreting totals or proposals.
Distinguish gross assets, liabilities, net worth, unrestricted cash, and restricted
or illiquid assets. Label unknown totals and partial coverage explicitly.
Do not describe securities or private investment marks as available cash.

Aggregate a security across included accounts using the actual security identity.
Confirm any mapping between share classes, ADRs, or listings before combining them.
The core aggregates exact symbols; it does not infer economic equivalence, fund
look-through exposure, sector classification, correlations, or option delta exposure.
Add such analysis only with sources and a stated method.

Read the user's actual limits. `null` means report only, not zero and not permission
to choose a threshold on their behalf. If the user explicitly sets a limit, update
only the relevant rule and record that confirmed choice with its date and source.
Explain observed concentration or leverage even when no threshold is configured.

## Evaluate a proposal

Capture account alias, security, side, quantity, proposed price, and as-of date.
Use [the proposal contract](references/review.md); keep the input in the private workspace.
Run `finance-core review --workspace /private/path --proposal /private/path/proposal.json`.
Report its status and reasons, including `needs_data` or report-only results.
The calculation uses a hypothetical cash-funded transaction and does not execute it.

Do not call a post-calculation limit flag a broker block or execution safeguard.
It also does not model taxes, fees, lot selection, slippage, settlement, or future
price paths. Research those separately when they affect the user's requested decision.
Unknown tax basis or jurisdiction cannot be replaced by an assumed zero tax cost.
State a proposal's funding source; do not infer margin authorization from buying power.

## Deliver and preserve the distinction

Lead with the material finding and its practical implication. Compare current and
proposed values on the same as-of date and valuation basis, with a short assumptions
table where useful. Cite the exact private snapshot, rules, and proposal files.
Separate measured facts, model-generated research, and your conditional assessment.

Save the review privately. Record an unaccepted idea only as `proposal`; a confirmed
decision still is not an executed trade. Reconcile actual fills through subsequent
account evidence before updating positions. No command in this workflow places orders.
