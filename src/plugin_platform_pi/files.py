"""What Pi is given at a start, as pure functions: its three files in its own agent folder, the permission step it
loads, and the words of its command line. Nothing is read, written or run here (the plugin writes what these make).

Each follows what C-P1 read in Pi 1.5.2's sources at the tag (packages/coding-agent/):

- models.json (`models_json`): one custom provider, `liminal`, the instance's OpenAI-compatible address with Pi's
  `openai-completions` API and the model with its context. Its apiKey is `${LIMINAL_SERVER_KEY}` where the server
  has a key, read by Pi from its environment at each request (core/resolve-config-value.ts), else the literal
  `none`: never the key itself, and never a value beginning with "!", which Pi would run as a command.
- mcp.json (`mcp_json`): Liminal's MCP alone, the MCP plugin's bridge as a stdio server whose environment names the
  token's variable (`${LIMINAL_MCP_TOKEN}`, resolved by Pi from its own), its timeout the MCP plugin's hold and a
  minute more; no server at all while Liminal's MCP is off.
- settings.json (`settings_json`): every folder's own .pi/ untrusted (defaultProjectTrust "never"), its install
  ping off a second time beside PI_TELEMETRY (enableInstallTelemetry), and on Windows its shell, Git for Windows'
  bash.exe by its whole path (shellPath), so Pi never asks `where bash.exe`.
- The permission step (`permission_ts`, PERMISSION): an extension of the plugin's own, loaded with -e. Pi asks nothing
  before a tool call by its makers' design; on its `tool_call` event (core/extensions/types.ts) the extension asks you
  on Pi's screen (ctx.ui.confirm) before every call that is not a read, and refuses the call ({block: true, reason})
  when you decline, when Pi has no screen to ask on (its print and json modes), and when a shell command is too long
  to be shown whole. A handler that throws blocks its tool too (C-P1.1).
- The command line (`arguments`): the permission step, the provider and the model, and --no-tools where Use… says
  the model calls none."""
from __future__ import annotations

import json
from typing import Iterable

from .constants import API, KEPT_SETTINGS, KEY_SAID, MCP_NAME, MCP_SECRET, NO_KEY, OUTPUT, PIN, PROVIDER

PERMISSION_VERSION = 1  # of the permission step's text (its first line says it)
SHOWN_MOST = 4000  # characters of a call shown in its question at the most: a longer shell command is refused
READS = ("read", "grep", "find", "ls")  # Pi's tools that only read: not asked
DECIDED_ELSEWHERE = f"mcp__{MCP_NAME}__"  # Liminal's MCP's tools: the MCP plugin grants and holds them itself
SHELLS = ("bash", "powershell")
UNSET = ("LIMINAL_MCP_TOKEN", "LIMINAL_SERVER_KEY")  # what an allowed shell command runs without


def text(data) -> str:
    """A file's text as the plugin writes it: JSON, two spaces, a line ending."""
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def output(context: int) -> int:
    """The most output named to Pi: a quarter of the context, OUTPUT at the most."""
    return max(1, min(OUTPUT, int(context) // 4))


def models_json(*, base_url: str, model: str, context: int, keyed: bool) -> dict:
    """models.json: providers.liminal, the instance's address, Pi's openai-completions API, a key named by its
    variable (or the literal `none`) and the one model with its context."""
    return {"providers": {PROVIDER: {
        "baseUrl": str(base_url),
        "api": API,
        "apiKey": KEY_SAID if keyed else NO_KEY,
        "models": [{"id": str(model), "name": str(model), "input": ["text"], "contextWindow": int(context),
                    "maxTokens": output(context)}],
    }}}


def mcp_json(argv: Iterable[str] | None = None, timeout_s: int = 0) -> dict:
    """mcp.json: Liminal's MCP alone where `argv` (the bridge's command) is given, else no server."""
    words = [str(w) for w in (argv or ())]
    if not words:
        return {"mcpServers": {}}
    return {"mcpServers": {MCP_NAME: {"command": words[0], "args": words[1:],
                                      "env": {MCP_SECRET: "${" + MCP_SECRET + "}"}, "timeout": int(timeout_s)}}}


def settings_json(*, system: str, shell_path: str = "", kept: dict | None = None) -> dict:
    """settings.json: what holds for every start, Pi's own note of the changelog it showed (KEPT_SETTINGS, from
    `kept`, what the file held) beside it, and on Windows its shell by its whole path."""
    out: dict = {}
    for name in KEPT_SETTINGS:
        value = (kept or {}).get(name)
        if isinstance(value, str) and value and len(value) <= 40 and value.replace(".", "").isalnum():
            out[name] = value
    out["defaultProjectTrust"] = "never"
    out["enableInstallTelemetry"] = False
    if system == "windows":
        if not shell_path:
            raise ValueError("on Windows Pi is given Git for Windows' bash by its whole path")
        out["shellPath"] = str(shell_path)
    return out


def arguments(*, extension: str, model: str, tools: bool) -> list[str]:
    """What follows Pi's program on its command line: its permission step, its one provider and the model, and
    --no-tools where the model calls none."""
    words = ["-e", str(extension), "--provider", PROVIDER, "--model", str(model)]
    if not tools:
        words.append("--no-tools")
    return words


def _js(value) -> str:
    """A value as JavaScript reads it (JSON's subset of it)."""
    return json.dumps(value, ensure_ascii=True)


PERMISSION = """\
// Liminal's permission step for Pi, v{version} (plugin-platform-pi {plugin}, for Pi {pi}).
// Written whole by the plugin at every start: an edit here lasts until the next one.
//
// Pi asks nothing before a tool call, by its makers' design. This extension asks you on Pi's screen before every
// call that is not a read: each shell command (bash, powershell), each edit and each write, and any other tool. A
// call you decline is not run, and the model is told so. Without a screen to ask on (Pi's print and json modes)
// every such call is refused, and so is a shell command too long to be shown whole.
// Not asked: its reads ({reads}), and Liminal's MCP tools ({elsewhere}*), which the MCP plugin
// grants and holds itself.
// A command you allow runs without Liminal's token and key in its environment ({unset}).

const READS = new Set({reads_js});
const DECIDED_ELSEWHERE = {elsewhere_js};
const SHELLS = new Set({shells_js});
const MOST = {most};
const UNSET = {unset_js};
const NO_SCREEN = "Liminal's permission step refused this call: Pi has no screen here to ask you on.";
const DECLINED = "The user declined this call (Liminal's permission step): it was not run. Ask before trying again.";

// control and direction characters made visible, so that what is asked cannot draw over its own question
function shown(value: unknown): string {{
  const said = typeof value === "string" ? value : value === undefined || value === null ? "" : String(value);
  const odd = /[\\u0000-\\u0008\\u000b-\\u001f\\u007f-\\u009f\\u200b-\\u200f\\u2028-\\u202e\\u2066-\\u2069\\ufeff]/g;
  return said.replace(odd, (c) => "\\\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}}

function cut(said: string): string {{
  if (said.length <= MOST) return said;
  return said.slice(0, MOST) + "\\n(" + (said.length - MOST) + " more characters not shown)";
}}

function described(name: string, input: any): string {{
  if (name === "write") {{
    const content = typeof input?.content === "string" ? input.content : "";
    return cut("Write " + shown(input?.path) + " (" + content.length + " characters):\\n" + shown(content));
  }}
  if (name === "edit") {{
    const edits = Array.isArray(input?.edits) ? input.edits : [];
    const parts = edits.map((e: any, i: number) =>
      "--- " + (i + 1) + ": replaces\\n" + shown(e?.oldText) + "\\n+++ with\\n" + shown(e?.newText));
    return cut("Edit " + shown(input?.path) + " (" + edits.length + " change" + (edits.length === 1 ? "" : "s") +
      "):\\n" + parts.join("\\n"));
  }}
  let given = "";
  try {{ given = JSON.stringify(input ?? {{}}, null, 1); }} catch {{ given = "(its input cannot be shown)"; }}
  return cut(shown(name) + ":\\n" + shown(given));
}}

export default function liminalPermission(pi: any) {{
  pi.on("tool_call", async (event: any, ctx: any) => {{
    const name = typeof event?.toolName === "string" ? event.toolName : "";
    if (READS.has(name) || (name.startsWith(DECIDED_ELSEWHERE) && name.length > DECIDED_ELSEWHERE.length)) {{
      return undefined;
    }}
    if (!ctx || !ctx.hasUI || !ctx.ui || typeof ctx.ui.confirm !== "function") {{
      return {{ block: true, reason: NO_SCREEN }};
    }}
    let question = "";
    if (SHELLS.has(name)) {{
      const command = typeof event?.input?.command === "string" ? event.input.command : "";
      if (command.length > MOST) {{
        return {{ block: true, reason: "Liminal's permission step refused this command: it is " + command.length +
          " characters, and only " + MOST + " can be shown whole to the user. Split it into shorter commands." }};
      }}
      question = "Run this " + name + " command?\\n" + shown(command) +
        "\\n(It runs as you, with no sandbox, without " + UNSET.join(" and ") + " in its environment.)";
    }} else {{
      question = described(name, event?.input);
    }}
    let yes = false;
    try {{
      yes = (await ctx.ui.confirm("Allow " + (shown(name) || "this tool") + "?", question,
                                  {{ signal: ctx.signal }})) === true;
    }} catch {{
      yes = false;
    }}
    if (!yes) {{
      return {{ block: true, reason: DECLINED }};
    }}
    if (name === "bash" && typeof event?.input?.command === "string") {{
      event.input.command = "unset " + UNSET.join(" ") + "\\n" + event.input.command;
    }} else if (name === "powershell" && typeof event?.input?.command === "string") {{
      event.input.command = UNSET.map((n: string) => "Remove-Item -ErrorAction SilentlyContinue Env:" + n).join("; ") +
        "\\n" + event.input.command;
    }}
    return undefined;
  }});
}}
"""


def permission_ts(plugin_version: str) -> str:
    """The permission step's text (TypeScript, which Pi loads by -e): written whole at every start."""
    return PERMISSION.format(
        version=PERMISSION_VERSION, plugin=plugin_version, pi=PIN, reads=", ".join(READS), elsewhere=DECIDED_ELSEWHERE,
        unset=", ".join(UNSET), reads_js=_js(list(READS)), elsewhere_js=_js(DECIDED_ELSEWHERE),
        shells_js=_js(list(SHELLS)), most=SHOWN_MOST, unset_js=_js(list(UNSET)))


__all__ = ["PERMISSION", "arguments", "mcp_json", "models_json", "output", "permission_ts", "settings_json",
           "text"]
