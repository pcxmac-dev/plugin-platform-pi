# Changelog

## 0.1.0 (2026-11-26)

The first release: Pi as one of the platform's top four open-source harnesses (the user, 2026-11-18: "top 4 inference
engines, top 4 agentic harnesses (open source)", "both linux and windows compatibility"; 2026-11-25, answers 7 and 8:
Pi "kept, with the plugin's own permission step before every shell command, edit and write", and the ports a tool
opens by itself said on its page). A harness on liminal-libs 1.66.0's AI bases (`Harness`, plugin API 2.2),
`SECTION = "ai"`, `GROUP = "harness"`, `order = 524`, `ICON = "pi"`: the standard interface of a harness, with no hook
of its own. Needs liminal-libs>=1.66.0.

- **Install, Update, Uninstall** from the page: Node.js 24.22.3 for this system (not pinned in this release: Install
  says so), Pi 1.5.2 by that node's own npm with no script run, its sha512 compared with the pin and its lock kept for
  `npm ci`, and ripgrep 15.1.0, pinned, placed where Pi looks. A musl Linux and an unknown processor are said. A Pi of
  yours is a fact, never run.
- **Use…, Open…, Command…** (the base's): one inference plugin's instance (all four engines), its model, and Pi's
  options (Context; Tools; Liminal's MCP).
- **Configured at launch**, nothing written into a Pi of yours: its own agent and sessions folders, `models.json`,
  `mcp.json` and `settings.json` written whole at each start (one provider, every folder untrusted, its install ping
  off, on Windows Git for Windows' bash by its whole path), offline (`PI_OFFLINE=1`, `PI_TELEMETRY=0`,
  `PI_SKIP_VERSION_CHECK=1`), the server's key in its environment alone.
- **Its permission step**: an extension of the plugin's own on Pi's `tool_call` event, asking on Pi's screen before
  every call that is not a read, refusing what you decline, what no screen can ask and a shell command too long to be
  shown whole, an allowed command run without Liminal's token and key.
- **Refused in words**: on Windows no Git for Windows' bash (WSL's launcher never used), a folder holding a program
  part of Pi would run from there, a value Pi would read as more than text (`$`, `${`, `$(`, a leading `!`), a context
  it is not told or under 8,192 tokens.
- **Its sessions** pruned to the newest 100 (200 MB at the most) as a window opens.
- **Liminal's MCP** through the MCP plugin's bridge, its token for each window alone.
- **Before you use it** on its page; four API cards (Pi, its configuration, npm's registry, Node.js); NEEDS rows in
  the getattr idiom.
