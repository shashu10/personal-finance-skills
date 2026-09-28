# Where your data goes

The financial workspace is stored on your computer, outside the source checkout. This
package has no telemetry and the core calculations do not make network requests.
File permissions are restrictive where the operating system supports them; the files
are not encrypted. Your own backup and cloud-sync settings still apply.

An agent reading files or using computer use may send their contents or screenshots to
its model provider. Local storage does not mean local inference. Account aliases reduce
identifier exposure but balances, share counts, and ratios can still be identifying.
Review your host's data controls and the permissions of each connector.

The explicit `context` exports have separate sharing switches in `rules.json`.
These switches govern the package's exporters, not what a general-purpose agent can
read through its own filesystem tools. TradingAgents requires exact quantities and
amounts; its exporter is disabled until that sharing choice is enabled.

Passwords, OAuth tokens, API secrets, session cookies, full account numbers, and identity
documents do not belong in the ledger, facts, decision log, or public bug reports. Keep
secrets in a keychain or provider-supported credential store. Use aliases such as
`broker-taxable-1`; keep any mapping to real identifiers in private connector settings.
The user completes login and two-factor prompts in the host's supported interface.

Computer-use collection is an assisted workflow, not a universal bank connector. The
skill prohibits trading, transfers, and account-setting changes during gathering. Use
actual read-only credentials or tool restrictions where the provider offers them;
natural-language instructions alone do not change a connector's permissions.

All tracked examples are synthetic. Before sharing a bug, reproduce it with synthetic
records. Do not upload statements or a real workspace to an issue. Run the public-source
check before committing, and inspect the exact diff: pattern checks cannot detect all
personal financial information or remove previously published Git history.
