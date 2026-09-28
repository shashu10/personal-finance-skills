# Public source boundary

This directory is an independent public repository inside a private multi-project workspace.
Only files under this directory belong to this project. Do not copy parent instructions,
personal configuration, statements, exports, reports, credentials, account identifiers,
wallet addresses, or sibling repository histories into it.

Use synthetic fixtures only. Real financial data belongs in an explicitly selected private
workspace outside this checkout. Missing data remains unknown; sample data is never a
fallback. Read neighboring code only when necessary to understand a reusable design, and
reimplement it without personal defaults.

Keep skill instructions short and focused. Shared deterministic behavior belongs in
`src/finance_core`. Optional upstream tools use supported interfaces and pinned revisions.
This project gathers information, calculates scenarios, and drafts research and proposals;
it has no order execution, money transfer, or email sending interface.

Before publication, run unit tests, skill validation, and the public-source audit. Review
the exact staged file list. Never stage or push from a parent directory.
