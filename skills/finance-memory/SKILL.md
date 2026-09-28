---
name: finance-memory
description: Save and retrieve confirmed personal financial facts, decisions, and their corrections in a private workspace with provenance and supersession. Use when the user provides an update, confirms a choice, or asks to resume prior financial planning.
---

# Finance memory

Preserve what the user established and decided, while keeping suggestions and unknowns
distinct. Files provide explicit continuity; do not claim hidden cross-chat memory
or automatic session hooks.

## Read before writing

Use the installed `finance-core` in its dedicated environment and selected private
workspace. Run `finance-core --help` if needed; this skill requires no sibling skill.
Read the private workspace's `setup.md` to resolve the configured interpreter. Run
the commands yourself; explain results and needed inputs in ordinary language.
Read `facts.json`, `decisions.json`, and relevant dated reports. Resolve `supersedes`
chains and inspect conflicts before answering from memory.

Read [memory records](references/records.md) for exact fields and examples.
Keep personal records, source notes, and input envelopes outside the public checkout.
Do not store credentials, authentication cookies, recovery codes, or unnecessary
personal identifiers. A private alias is usually enough.

## Classify the update

- A fact is a user-confirmed statement with a date and source. Preserve whether the
  user reported it directly or confirmed a document's contents.
- A proposal is an idea or recommendation. It is not an accepted decision.
- A confirmed decision requires explicit user acceptance, including acceptance
  already present in the conversation; do not ask for it again.
- An executed decision requires evidence of completion or an explicit user report
  of completion. Preserve that source; a requested action or prepared order is not a fill.

Tax interpretations, model forecasts, and guessed preferences are not personal facts.
Save them in a dated research/scenario report or as an unconfirmed proposal.
If a user shares a fact during an authorized intake or asks to remember it, save
their actual statement without adding assumptions or requesting duplicate confirmation.
Ask only when the status, meaning, or material conflict cannot be resolved from context.

## Save without rewriting history

Use stable IDs. Repeating identical records is idempotent; a changed record with the
same ID is a conflict. Correct a record with a new ID and `supersedes` pointing to
the old one. Explain the correction and effective date, and retain its source.
For changed decisions, distinguish a new preference from correction of an old error.

Prepare a private envelope containing `facts` and/or `decisions`, then run:
`finance-core memory --workspace /private/path --input /private/path/update.json`.
Run `finance-core validate --workspace /private/path` and inspect the saved records.
The confirmation field records supplied evidence; the CLI cannot independently prove
user consent or a transaction. Do not set it true to bypass a validation error.

Memory changes do not update balances or execute choices. Use sourced account imports
for positions and cash. A newly reported purchase can be saved as a user-reported
execution while the ledger remains awaiting reconciliation; state that distinction.

## Use memory in later work

Prefer the latest applicable confirmed fact or decision. Explain contradictions
instead of merging them into a new invented story. Preserve dates and conditional
choices, such as a plan that applies only after a job starts or a debt is repaid.
Review facts whose circumstances or rules may have changed before using them again.

Model-sharing rules govern exports, not memory storage. Saving a sensitive fact
does not authorize uploading the file to another service or a separate model API.
Reading it in a hosted agent can itself send its contents to that agent's provider;
the export switches do not restrict the host's filesystem or computer-use tools.
If the user asks for deletion, inspect the affected records and references and
follow the authorized removal request; append-only correction is not a prohibition
on deleting the user's private data.

## Report the result

Summarize what was saved, superseded, left unresolved, or kept as a proposal.
Link the actual private files and state any remaining reconciliation need.
Do not announce reminders, scheduled reviews, broker changes or future automatic
updates unless they were separately requested and actually configured.
