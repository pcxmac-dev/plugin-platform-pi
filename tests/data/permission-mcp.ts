// Liminal's permission step for Pi, v1 (plugin-platform-pi 0.1.0, for Pi 1.5.2).
// Written whole by the plugin at every start: an edit here lasts until the next one.
//
// Pi asks nothing before a tool call, by its makers' design. This extension asks you on Pi's screen before every
// call that is not a read: each shell command (bash, powershell), each edit and each write, and any other tool. A
// call you decline is not run, and the model is told so. Without a screen to ask on (Pi's print and json modes)
// every such call is refused, and so is a shell command too long to be shown whole.
// Not asked: its reads (read, grep, find, ls), and Liminal's MCP tools (mcp__liminal__*), which the MCP plugin
// grants and holds itself.
// A command you allow runs without Liminal's token and key in its environment (LIMINAL_MCP_TOKEN, LIMINAL_SERVER_KEY).

const READS = new Set(["read", "grep", "find", "ls"]);
const DECIDED_ELSEWHERE = "mcp__liminal__";
const SHELLS = new Set(["bash", "powershell"]);
const MOST = 4000;
const UNSET = ["LIMINAL_MCP_TOKEN", "LIMINAL_SERVER_KEY"];
const NO_SCREEN = "Liminal's permission step refused this call: Pi has no screen here to ask you on.";
const DECLINED = "The user declined this call (Liminal's permission step): it was not run. Ask before trying again.";

// control and direction characters made visible, so that what is asked cannot draw over its own question
function shown(value: unknown): string {
  const said = typeof value === "string" ? value : value === undefined || value === null ? "" : String(value);
  const odd = /[\u0000-\u0008\u000b-\u001f\u007f-\u009f\u200b-\u200f\u2028-\u202e\u2066-\u2069\ufeff]/g;
  return said.replace(odd, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}

function cut(said: string): string {
  if (said.length <= MOST) return said;
  return said.slice(0, MOST) + "\n(" + (said.length - MOST) + " more characters not shown)";
}

function described(name: string, input: any): string {
  if (name === "write") {
    const content = typeof input?.content === "string" ? input.content : "";
    return cut("Write " + shown(input?.path) + " (" + content.length + " characters):\n" + shown(content));
  }
  if (name === "edit") {
    const edits = Array.isArray(input?.edits) ? input.edits : [];
    if (edits.length === 0) {
      let given = "";
      try { given = JSON.stringify(input ?? {}, null, 1); } catch { given = "(its input cannot be shown)"; }
      return cut("Edit " + shown(input?.path) + ", as it was given:\n" + shown(given));
    }
    const parts = edits.map((e: any, i: number) =>
      "--- " + (i + 1) + ": replaces\n" + shown(e?.oldText) + "\n+++ with\n" + shown(e?.newText));
    return cut("Edit " + shown(input?.path) + " (" + edits.length + " change" + (edits.length === 1 ? "" : "s") +
      "):\n" + parts.join("\n"));
  }
  let given = "";
  try { given = JSON.stringify(input ?? {}, null, 1); } catch { given = "(its input cannot be shown)"; }
  return cut(shown(name) + ":\n" + shown(given));
}

export default function liminalPermission(pi: any) {
  pi.on("tool_call", async (event: any, ctx: any) => {
    const name = typeof event?.toolName === "string" ? event.toolName : "";
    const elsewhere = DECIDED_ELSEWHERE !== "" && name.startsWith(DECIDED_ELSEWHERE) &&
      name.length > DECIDED_ELSEWHERE.length;
    if (READS.has(name) || elsewhere) {
      return undefined;
    }
    if (!ctx || !ctx.hasUI || !ctx.ui || typeof ctx.ui.confirm !== "function") {
      return { block: true, reason: NO_SCREEN };
    }
    let question = "";
    if (SHELLS.has(name)) {
      const command = typeof event?.input?.command === "string" ? event.input.command : "";
      if (command.length > MOST) {
        return { block: true, reason: "Liminal's permission step refused this command: it is " + command.length +
          " characters, and only " + MOST + " can be shown whole to the user. Split it into shorter commands." };
      }
      question = "Run this " + name + " command?\n" + shown(command) +
        "\n(It runs as you, with no sandbox, without " + UNSET.join(" and ") + " in its environment.)";
    } else {
      question = described(name, event?.input);
    }
    let yes = false;
    try {
      yes = (await ctx.ui.confirm("Allow " + (shown(name) || "this tool") + "?", question,
                                  { signal: ctx.signal })) === true;
    } catch {
      yes = false;
    }
    if (!yes) {
      return { block: true, reason: DECLINED };
    }
    if (name === "bash" && typeof event?.input?.command === "string") {
      event.input.command = "unset " + UNSET.join(" ") + "\n" + event.input.command;
    } else if (name === "powershell" && typeof event?.input?.command === "string") {
      event.input.command = UNSET.map((n: string) => "Remove-Item -ErrorAction SilentlyContinue Env:" + n).join("; ") +
        "\n" + event.input.command;
    }
    return undefined;
  });
}
