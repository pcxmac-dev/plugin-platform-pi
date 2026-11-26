# plugin-platform-pi

Pi for Liminal: Pi's open-source coding agent in the terminal (`@earendil-works/pi-coding-agent`), installed pinned on
a Node.js of its own into the platform's own folder, configured against one instance of an inference plugin's, and
opened in a folder you pick. Pi itself asks nothing before a tool call and has no sandbox, by its makers' design: this
plugin's own permission step asks you on Pi's screen before every shell command, edit and write.

The user's words: 2026-11-18, "top 4 inference engines, top 4 agentic harnesses (open source)", "all platform", "both
linux and windows compatibility"; 2026-11-25, answer 7, Pi "kept, with the plugin's own permission step before every
shell command, edit and write"; answer 8, the ports a tool opens by itself said on its page.

## What it does

A harness (`liminal_libs.machines.harness.Harness`, liminal-libs 1.66.0, plugin API 2.2), drawn under the platform's AI
plugins, Harnesses, at 524 (OpenCode 520, Aider 521, Continue 522, Codex CLI 523, goose 525), its icon Pi's own mark
(`pi`). It is middleware of that kind: the standard interface of a harness, with no hook of its own. Valid wherever it
runs: what a system lacks is a fact and a refusal in words.

- **Install, Update, Uninstall**, each from the page, Install a job with its size, its hosts and its licences said
  first and the licence accepted in a second confirmation. Three pieces go into `app/1.5.2`:
  - **Node.js 24.22.3** for this system (`node-v24.22.3-win-x64.zip`, `node-v24.22.3-linux-x64.tar.xz` and their
    arm64 builds) from `nodejs.org`, unpacked into `node/`. **None is pinned in this release**: their sizes and
    sha256 (nodejs.org's `SHASUMS256.txt`) were not read before it was built, so Install says so and installs
    nothing until a release pins them. Node.js publishes no build for a musl Linux (Alpine's): there the page says so.
  - **Pi 1.5.2**, put into `cli/` by that node's own npm (`liminal_libs.machines.node`), word for word
    `npm install --prefix cli --save-exact --ignore-scripts --no-audit --no-fund --no-update-notifier
    @earendil-works/pi-coding-agent@1.5.2`, from `registry.npmjs.org`, with an empty npmrc and none of your npm or
    Node.js settings, proxies or provider keys. Its sha512 (npm's `dist.integrity`, `sha512-mUWI04rq…5yA==`) is
    compared with the one npm's lock records before anything is put in use. Its dependencies are resolved by npm on
    the day and checked against the registry's own sums alone: none of them is pinned in this plugin. The lock is
    kept in `config/npm/`, and a reinstall of the same pin installs exactly those packages again with `npm ci`.
  - **ripgrep 15.1.0** (Pi's grep tool's and its commands' `rg`), from `github.com` (sent on to
    `release-assets.githubusercontent.com`), pinned by name, size and sha256 as plugin-platform-opencode pins it,
    into `bin/`. fd (Pi's `@` completion and its find tool, off unless asked) is not pinned in this release.
  A Pi of yours (on PATH, `~/.pi`) is left as it is, never run. Never run from here: `pi install`, `pi update`,
  `/login`, `/share`, any package's install script.
- **Use…, Open…, Command…** (the base's): one inference plugin's instance and its model, with Pi's options (Context;
  Tools: auto, yes or no; Liminal's MCP). All four engines qualify: Pi asks an OpenAI-compatible server's chat
  completions API. Open… opens Pi in a window of its own where there is a desktop, the lines to paste elsewhere.

### How Pi is started

- **That node with Pi's `dist/bundle/cli.js`**, by their whole paths (never npm's `pi.cmd`, never a node on PATH),
  then `-e <the permission step> --provider liminal --model <the model>` and `--no-tools` where the model calls none.
- **Its own folders**, under `<home>/config/pi`: `agent/` is `PI_CODING_AGENT_DIR`, `sessions/` is
  `PI_CODING_AGENT_SESSION_DIR`, `compile-cache/` is `NODE_COMPILE_CACHE` (nothing in the temporary folder).
- **Its files, written whole at every start** (`files.py`):
  - `models.json`: one provider, `liminal`, the instance's address with Pi's `openai-completions` API, the model with
    its context and a quarter of it (8,192 at the most) as its output. Its `apiKey` is `${LIMINAL_SERVER_KEY}` where
    the server has a key, which Pi reads from its environment at each request, else the literal `none`: never the key
    itself, and never a value beginning with `!`, which Pi would run as a command.
  - `mcp.json`: no server, or Liminal's MCP alone (below).
  - `settings.json`: `defaultProjectTrust: "never"` (a folder's own `.pi/` settings, MCP servers and extensions are
    never loaded), `enableInstallTelemetry: false`, and on Windows `shellPath`, Git for Windows' `bash.exe` by its
    whole path. Only Pi's own note of the changelog it last showed is kept of what the file held.
  - The permission step, `config/pi/liminal/permission.ts`, outside the agent folder's `extensions/` (which Pi would
    load a second time).
- **Offline**: `PI_OFFLINE=1` (no model catalogue from pi.dev, no version check, no package install, no download of fd
  or ripgrep), `PI_TELEMETRY=0` (no install ping) and `PI_SKIP_VERSION_CHECK=1`. Each request still carries Pi's
  `User-Agent`.
- **What it inherits**: every pair of Liminal's dropped, every hosted provider's key and settings, every `PI_*`,
  `NODE_*` and `npm_config_*` of yours; a PATH without relative or empty entries; on Windows
  `NoDefaultCurrentDirectoryInExePath=1`, so the programs Pi runs by name are looked up on PATH alone. The server's key
  is in `LIMINAL_SERVER_KEY` alone, a secret of the launch.

### Its permission step

Pi's extension API holds a tool call until its handler answers (C-P1.1: the `tool_call` event, awaited with no
timeout; a handler that throws blocks the tool). The plugin's extension, loaded with `-e` at every start:

- asks you on Pi's screen (`ctx.ui.confirm`, which Escape closes) before each call that is not a read: each shell
  command (`bash`, `powershell`), each `edit` and each `write`, and any other tool, showing what would run (control
  and direction characters shown as `\uXXXX`, so what is asked cannot draw over its question);
- refuses the call (`{block: true, reason}`) when you decline, when Pi has no screen to ask on (its print and json
  modes), and when a shell command is longer than 4,000 characters, too long to be shown whole;
- lets Pi's reads (`read`, `grep`, `find`, `ls`) run without asking: they read whatever you can read; and, only for a
  start with Liminal's MCP on, Liminal's MCP tools (`mcp__liminal__*`), which the MCP plugin grants and may hold for
  your answer on its own page (with it off, an MCP tool is asked like any other);
- shows an edit whole as it was given where its input is not in Pi 1.5.2's shape (`edits: [{oldText, newText}]`);
- runs an allowed command without `LIMINAL_MCP_TOKEN` and `LIMINAL_SERVER_KEY` in its environment (it is told so).

What you allow runs at once with your rights, with no sandbox, including commands that reach this machine's platform.
The commands you type yourself after `!` are yours and are not asked.

### Before you use it (its page)

- What it asks before it acts, in Pi's makers' words and the plugin's.
- **Local only**: its one provider, the three switches, what is dropped, its `User-Agent`.
- **/share and /bug**: they send a session to its makers' services (/share as a GitHub gist through `gh`) when you type
  them. Nothing does so by itself.
- **The folder's .pi and AGENTS.md**: `.pi/` is never loaded; its `AGENTS.md` or `CLAUDE.md`, and those of every folder
  above it, are, as Pi loads them whatever the trust. Pi stops that only by a switch of its command line,
  `--no-context-files`, which also drops the agent folder's own AGENTS.md; it is not passed from here (the plan's
  choice, said on the page).
- **Its shell**: on Windows Git for Windows' bash, looked for in `%ProgramFiles%\Git\bin`, `%ProgramFiles(x86)%\Git\bin`
  and `%LOCALAPPDATA%\Programs\Git\bin`. Without it Pi is not started, and installing Git for Windows is yours to do.
  The `bash.exe` of `System32`, `Sysnative` or `WindowsApps` is WSL's launcher, which would run Pi's commands inside a
  WSL distribution: it is never used from here, even first on PATH. A folder holding at its top a program part of Pi
  would run from there before PATH (`where`, `bash`, `pwsh`, `powershell`, `fd`, `fdfind`, `rg`, `git`, `taskkill`,
  `tar`, `npm`, `node`, `gh`, `clip`, `rundll32`, `cmd`, with each ending Windows runs) is not opened from here.
  Windows Terminal draws its screen best. On Linux, `/bin/bash`.
- **Its Node.js** and **its tools**, as above.
- **Its ports**: none opened by itself here. Only a sign-in to a hosted provider (`/login`, never run from here) or to
  an MCP server (none of Liminal's asks one) would listen on this machine's own loopback while it lasts.
- **Its sessions**: Pi saves every session (your prompts, its answers, the commands it ran and what they said) in its
  sessions folder. The plugin keeps the newest 100 (200 MB at the most) and removes older ones as each Open… opens a
  window, while none of its windows is open; Command… removes nothing.
- The model and its context; a key, plain http and Liminal's MCP where they apply; what it shares with a Pi of yours;
  its configuration.

### Liminal's MCP

Off unless Use… turns it on. Then each window reaches it through the MCP plugin's bridge, a stdio server of Pi's
`mcp.json` (`liminal`), whose `env` names `${LIMINAL_MCP_TOKEN}`, resolved by Pi from its own environment, where a
token for that window alone is put; it is ended once the window is gone. Command… asks no token. Pi's MCP timeout is
the MCP plugin's hold and a minute more. The bridge must be named by a whole path (Pi's cross-spawn looks a bare name
up in the folder first). The commands you allow run without the token, but a program running as you could still read
Pi's own environment: the MCP plugin's grants decide what it may list and call.

## Not yet confirmed by a real run

Everything here is tested on stand-ins alone: nothing was downloaded, installed or started.

- Node.js 24.22.3's archives, their sizes and sums (none pinned in this release), and npm 11 run as that node.
- Pi 1.5.2 as npm installs it: its tree, its lock's sha512, `npm ci` from the kept lock.
- Pi reading `models.json` as written (`models`, `contextWindow`, `maxTokens`, `input`), `--provider` and `--model`
  choosing it, and `--no-tools`.
- The permission step loaded by `-e` as TypeScript, its question on Pi's screen, Escape closing it, a declined call
  refused with its reason, and the `unset` line before an allowed command in Git Bash.
- That MCP tools reach the `tool_call` event (C-P1 inferred it from Pi's pipeline, did not run it).
- `shellPath` taken, `where bash.exe` never run, and `NoDefaultCurrentDirectoryInExePath` honoured by `where.exe`
  (Microsoft documents only that `where` searches the folder and PATH).
- ripgrep found in the agent folder's `bin/`, and no download or PATH probe of it; Pi's `fd` probe on PATH.
- Liminal's MCP through the bridge with Pi's MCP client (it asks for revision 2025-11-25).
- A window on Linux, WSLg among them.

## The pins

- Pi 1.5.2: npm's `latest` of 2026-11-10, its SLSA provenance naming the tag `v1.5.2` (commit `b4afdddf`), MIT. Its
  unpacked size is 24,401,012 bytes; the tarball's own size is not in npm's record.
- Node.js 24.22.3, the newest of its line when the checks were made (2026-11-10): MIT and the licences its LICENSE
  names.
- ripgrep 15.1.0: Unlicense or MIT.

## Tests

```
python -m pytest -q
```

Stand-ins only, under the library's guard (no process, socket or name lookup): the web, npm, the window, the login and
the platform. `LIMINAL_VENDOR_PAGES=1` alone asks every page its API cards link.
