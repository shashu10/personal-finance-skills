# Where your data goes

Your financial workspace stays on your computer, outside the source checkout. This
package has no telemetry and the core calculations do not make network requests.
File permissions are restrictive where the operating system supports them; the files
are not encrypted. Your own backup and cloud-sync settings still apply.

An agent that reads files or operates your computer may send file contents or screenshots
to its model provider, even when you store the records locally. Account aliases limit
exposure of identifiers, but balances, share counts, and ratios can still identify you.
Review your host's data controls and the permissions of each connector.

The explicit `context` exports have separate sharing switches in `rules.json`.
These switches control the package's exporters. They do not restrict what an agent can
read through its own filesystem tools. TradingAgents requires exact quantities and
amounts; its exporter stays disabled until you enable that sharing choice.

Passwords, OAuth tokens, API secrets, session cookies, full account numbers, and identity
documents do not belong in the ledger, facts, decision log, or public bug reports. Keep
secrets in a keychain or provider-supported credential store. Use aliases such as
`broker-taxable-1`; keep any mapping to real identifiers in private connector settings.
The user completes login and two-factor prompts in the host's supported interface.

The skill guides an agent through account pages using available computer-use tools;
it does not provide a universal bank connector. It prohibits trading, transfers, and
account-setting changes during gathering. Use actual read-only credentials or tool
restrictions where the provider offers them;
natural-language instructions alone do not change a connector's permissions.

All tracked examples are synthetic. Before sharing a bug, reproduce it with synthetic
records. Do not upload statements or a real workspace to an issue. Run the public-source
check before committing, and inspect the exact diff: pattern checks cannot detect all
personal financial information or remove previously published Git history.
