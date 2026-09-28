# Runtime setup for the agent

Run these steps with your own tools. The user should be able to ask for setup, a
summary, or a scenario without learning Python commands. The examples below describe
implementation steps, not a checklist to hand back to the user.

## Reuse before installing

Check for the private workspace's `setup.md`, an existing configured interpreter,
the active project's applicable `AGENTS.md`, or a working `finance-core --help`.
For project-specific commands, read [project integration](project.md).
Reuse a trusted development checkout and its environment when the user is already
working on this project. Resolve paths explicitly
instead of changing global PATH or installing into an unrelated Python environment.

The `npx skills add` installer copies skill folders and references. It does not install
the shared Python package or guarantee a local source checkout.
If only this skill folder exists, obtain the source from the
[official repository](https://github.com/shashu10/personal-finance-skills).

## First installation

Use Python 3.11 or newer, Git, and an isolated environment. Check available tools first.
If a prerequisite is missing, use the host's supported setup tools within the user's
authorization; otherwise explain the specific missing capability. Do not claim success
or fabricate financial results when tools cannot run.

Choose a persistent tools directory separate from the user's financial workspace and
installed skill folders, for example `~/.local/share/personal-finance-skills-tools`.
Use an appropriate per-user location on Windows. Never overwrite an existing unrelated
directory or reset a modified source checkout. If no trusted checkout exists, fetch it:

```text
git clone https://github.com/shashu10/personal-finance-skills.git /absolute/tools/source
git -C /absolute/tools/source rev-parse HEAD
```

Inspect `pyproject.toml` and record the full source revision. Then create a dedicated
environment and install the helpers from that source:

```text
python3 -m venv /absolute/tools/runtime
/absolute/tools/runtime/bin/python -m pip install /absolute/tools/source
/absolute/tools/runtime/bin/python -m finance_core --help
```

Replace `python3` with the verified interpreter. On Windows, use
`/absolute/tools/runtime/Scripts/python.exe` for the environment's interpreter.
Prefer a normal install; an editable install is appropriate when the user
is developing the source. No broker credentials or model keys are needed for this step.

Before recommending or installing an optional skill found in a directory, check its
actual source revision, `SKILL.md` path, referenced files and supported prerequisites.
A search listing may still point to a renamed or removed file. Report a stale listing
instead of substituting an unrelated skill with a similar name.

## Create and verify the private workspace

Reuse an existing workspace or select a new private directory outside the source
checkout. Ask for the base currency if it is unknown; do not infer residence from it.
Using the environment's Python, run:

```text
python -m finance_core init --workspace /private/finances --base-currency USD
python -m finance_core validate --workspace /private/finances
```

Here and below `python` means the verified environment's absolute interpreter path;
the path and currency are illustrative. An existing POSIX workspace must be private
(mode 0700). If it is not, choose a dedicated directory instead of changing an unrelated
folder's permissions. Do not initialize over the user's existing ledger in another format.

Save `setup.md` in the private workspace with the source URL/revision, source directory,
interpreter path, workspace path, base currency, and any verified project adapters.
Do not include credentials. Later skills can use that note to call the helpers without
asking the user to manage paths.

Keep risk limits unset until the user chooses them. Leave model-context sharing off
until the user authorizes the relevant export. Optional TradingAgents and Vibe-Trading
installations follow the fetched source's `docs/integrations.md` only when needed.

## Diagnose an existing setup

Use the paths recorded in `setup.md`. Check only what the requested task needs and
report the working command or the specific failure:

| Component | Check |
| --- | --- |
| Skills | Confirm the selected agent can discover the installed skill and its references. A linked development copy may differ from a global installed copy. |
| Runtime | Run the recorded interpreter with `-m finance_core --help`. Resolve an import error before changing unrelated environments. |
| Source | Inspect the recorded checkout revision and working-tree status. Retain local edits. |
| Workspace | Run `finance_core validate` and `summary` through that interpreter, with the recorded workspace and reporting date. Distinguish valid files from complete, fresh account coverage. |
| Optional engine | Inspect the selected engine's installer receipt/version, documented help, provider choices and output path. Use its dry run when supported; do not contact accounts or launch a paid model merely to check installation. |

Use the existing project adapter where one is recorded. A missing optional engine
does not prevent a spending review or ledger calculation. Diagnosis does not initialize
a replacement workspace, change sharing permissions, or synchronize accounts.

## Update the intended component

An `npx skills` installation and the Python runtime have separate update paths.
Updating skill folders does not upgrade the calculation package or optional engines.

When the user asks to update installed skills, inspect `npx skills update --help` for
the installed CLI, select this bundle's skill names and the intended scope, and review
any local changes before replacement. A linked development checkout is maintained in
its own repository; do not replace those links with downloaded copies inadvertently.

For a runtime update, inspect the trusted source checkout and proposed revision first.
Preserve local edits and read any compatibility or migration notes. Back up the private
workspace before a change that could affect its format. Install the reviewed source
into the recorded environment using that environment's interpreter, then verify its
help, validate the existing workspace, and compare the same dated summary. A successful
package install alone does not establish financial-data compatibility.

Optional engine revisions are recorded in the trusted checkout's `integrations.json`.
Update only the engine needed for the requested workflow, using its separate managed
environment and installer checks. Keep provider/model choices and credentials intact.
Do not upgrade to an arbitrary upstream branch to repair a missing API key.

Record the resulting source revision, runtime path, engine versions and checks in
`setup.md`, along with what update the user requested. Run updates within that request;
do not add background updates or reinstall working tools during routine research.
Preserve the prior setup details when a check fails, and report the failure.
Never reset a modified checkout, migrate an unrelated ledger, or silently change
financial rules as part of an update.

## Prompt-driven demo and calculations

If the user asks for a demonstration, initialize a separate new workspace with `--demo`.
Never add demonstration records to their real workspace. You can then run:

```text
python -m finance_core init --workspace /private/finance-demo --demo
python -m finance_core validate --workspace /private/finance-demo
python -m finance_core summary --workspace /private/finance-demo
python -m finance_core plan --workspace /private/finance-demo --monthly-expenses 3200 --monthly-income 2000 --one-time-cost 1500
```

Explain the resulting sample balance sheet and runway in ordinary language. For a real
question, replace the illustrative amounts with confirmed or clearly labeled scenario
inputs and cite the actual private records. Do not show shell commands unless the user
asks for technical details or needs to perform a step the host cannot complete.
