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
