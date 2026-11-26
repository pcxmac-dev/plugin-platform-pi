"""What the Pi plugin says on its page: constants and pure functions, nothing read, run or asked here.

`rows(...)` is the table "Before you use it" (what Pi does that a user should know before a start, each in a row of
its own), `open_words(...)` the sentences Open…'s confirmation ends with, and the rest the words of a fact, a refusal
or the install. Each sentence follows what was read in Pi 1.5.2's sources and on its makers' pages (the pre-build
checks, C-P1; constants.py names them)."""
from __future__ import annotations

from typing import Iterable

from liminal_libs.machines import node

from .constants import (FD, FEWEST, MCP_NAME, MCP_SECRET, NODE_VERSION, PIN, RIPGREP, SECRET, SESSIONS_BYTES,
                        SESSIONS_KEPT)
from .files import READS

ABOUT = "Pi's open-source coding agent, started against a local model server, asking before each command and edit"
TABLE = "Before you use it"
COLUMNS = [{"title": "What"}, {"title": "Said"}]
NO_SERVER = "the model server you choose (Use…)"
CHECKED = (f"Node.js {NODE_VERSION}'s archive and ripgrep {RIPGREP}'s are checked against the sha256 pinned in this "
           "plugin. " + node.checked_words("Pi"))
ASKS = ("Pi itself asks nothing before a tool call and has no sandbox: in its makers' words it does not ask for "
        "approval before every tool call. This plugin's own permission step (an extension it writes and Pi loads at "
        "every start from here) asks you on Pi's screen before each shell command, each edit, each write and every "
        f"other tool, showing what would run; a call you decline is not run. Its reads ({', '.join(READS)}) are not "
        "asked, and read whatever you can read. What you allow runs at once with your rights, with no sandbox, "
        "including commands that reach this machine's platform, whose API runs what you can run. The commands you "
        "type yourself after ! are yours and are not asked.")
LOCAL = ("The one model server it is given is {server}, as a provider of its own (liminal). It is started offline "
         "(PI_OFFLINE=1): no model catalogue from pi.dev, no version check, no package installs and no download of "
         "fd or ripgrep. Its install ping is off twice (PI_TELEMETRY=0, and enableInstallTelemetry in its settings), "
         "and PI_SKIP_VERSION_CHECK=1. Every pair of Liminal's is dropped from what it inherits, every hosted "
         "provider's key, every PI_* and your Node.js and npm settings too. Each request still carries Pi's "
         "User-Agent (its version, this system, its Node.js).")
SHARE = ("Its /share and /bug commands send a session to its makers' services (/share through gh, as a GitHub gist) "
         "when you type them. Nothing does so by itself.")
FOLDER = ("A folder's own .pi/ (its settings, MCP servers and extensions) is not loaded: every folder is untrusted "
          "here (defaultProjectTrust: never). Its AGENTS.md or CLAUDE.md, and those of every folder above it, are "
          "loaded all the same, as Pi loads them whatever the trust; Pi stops that only by a switch of its command "
          "line (--no-context-files), which is not passed from here.")
WINDOWS = ("On Windows its commands run in Git for Windows' bash, {bash}, given to Pi by its whole path. The bash.exe "
           "of System32 or WindowsApps is WSL's launcher, which would run them inside a WSL distribution: it is never "
           "used from here. Pi looks for the programs it runs by name (git, rg, fd, its shells) on PATH alone "
           "(NoDefaultCurrentDirectoryInExePath), and a folder holding one of them at its top is not opened from "
           "here, since part of Pi would run that one. Windows Terminal draws its screen best.")
NO_BASH = ("On Windows Pi needs Git for Windows' bash, and none is installed where Git for Windows puts it: {paths}. "
           "Installing Git for Windows is yours to do. The bash.exe on PATH is WSL's launcher, which would run Pi's "
           "commands inside a WSL distribution: it is never used from here.")
LINUX = "On Linux its commands run in /bin/bash (else the first bash on PATH, else sh)."
NODE = (f"It runs on a Node.js {NODE_VERSION} of its own (Node.js 24, its long-term line), never on one of yours. Pi "
        f"{PIN} and the packages npm resolved for it are in the plugin's folder; " "{deps}")
TOOLS = (f"ripgrep {RIPGREP} (its grep tool's and its commands' rg) is placed where Pi looks before PATH, so Pi never "
         "downloads its own. " + ("fd is not pinned in this release: Pi looks for one on PATH for its @ completion "
                                  "and its find tool (off unless asked), and downloads none while offline."
                                  if not FD else f"fd {FD} is placed beside it."))
PORTS = ("It opens no port by itself here. Only a sign-in to a hosted provider (/login, never run from here) or to an "
         "MCP server (none of Liminal's asks one: it takes a token) would listen on this machine's own loopback while "
         "it lasts.")
SESSIONS = ("Pi saves every session (your prompts, its answers, the commands it ran and what they said) under "
            "{sessions}. The plugin keeps the newest "
            f"{SESSIONS_KEPT} ({SESSIONS_BYTES // 1_000_000} MB at the most) "
            "and removes older ones as each Open… opens a window, while none of its windows is open.")
MODEL = "Pi asks the model server's chat completions API (/v1/chat/completions) and needs a model that calls tools."
SHARED = ("This copy has its own program and its own folders ({agent}: PI_CODING_AGENT_DIR): nothing is read from or "
          "written into {theirs}, and a Pi of yours is never run.")
THEIRS = {"windows": "%USERPROFILE%\\.pi", "linux": "~/.pi"}
CONFIGURED = ("models.json, mcp.json and settings.json in {agent} and the permission step ({extension}) are written "
              "whole at each start (an edit there lasts until the next one), and the model is named on its command "
              "line, so a window still open keeps its server.")
PLAIN = "{server} is asked over plain http on another machine: prompts and code can be read on the way."
KEYED = ("{server}'s key reaches Pi in its environment alone (" + SECRET + ", which its provider's apiKey names), "
         "never in a file or on its command line.")
MCP = (f"With Liminal's MCP on (under Use…), each window reaches it through the MCP plugin's bridge, an MCP server "
       f"of Pi's ({MCP_NAME}), with a token for that window alone in Pi's environment ({MCP_SECRET}, which its "
       "mcp.json entry names), ended once the window is gone. The commands you allow run without it, but a program "
       "running as you could still read Pi's own environment. What it may list and call is granted on the MCP plugin's page, "
       "which may hold a call for your answer there: Pi waits as long as the MCP plugin holds it, and a minute more.")


def row(what: str, said: str) -> list[str]:
    return [what, said]


def joined(names: Iterable[str]) -> str:
    """Names in words: "a", "a and b", "a, b and c"."""
    shown = [str(n) for n in names if str(n)]
    return shown[0] if len(shown) < 2 else ", ".join(shown[:-1]) + " and " + shown[-1]


def context_words(server: str, model: str, *, typed: int | None, known: int | None, used: int | None) -> str:
    """What Pi is told of the model's context, in words: the context it is given and where it comes from, or why it
    cannot be started; the server's own word beside a larger one typed under Use…."""
    if used is None:
        return f"{server} does not say {model}'s context: give it under Use… (Context) first."
    if used < FEWEST:
        return (f"A context of {used:,} tokens is under the {FEWEST:,} Pi is started with here: give the real one "
                f"under Use…, or start {server} with more.")
    whence = "given under Use…" if typed else f"as {server} says it"
    said = f"It is told {used:,} tokens of context ({whence})."
    if typed and known and typed > known:
        said += (f" You gave {typed:,} under Use…, and {server} says {model} has {known:,} there: Pi would fill more "
                 "than the server holds.")
    return said


def tools_words(told: bool, listed: bool | None, option: str) -> str:
    if not told:
        return "It is started with no tools (Use…, Tools: no): it can answer, not act."
    if listed is False and option == "yes":
        return "Its server says the model calls no tools, and Use… says it does (Tools: yes)."
    return ""


def rows(*, server: str, model: str, system: str, agent: str, sessions: str, extension: str, bash: str,
         bash_paths: Iterable[str], typed: int | None, known: int | None, used: int | None, tools: str, keyed: bool,
         plain: bool, yours: str, chosen: bool, mcp: bool, deps: str) -> list[list[str]]:
    """The rows of Before you use it, in the order a user reads them: what it asks before it acts, what stays local,
    its /share and /bug, the folder's .pi/ and its AGENTS.md, its shell, its Node.js, its tools, its ports, its
    sessions, the model, what it shares with a Pi of yours, its configuration; a key, plain http and Liminal's MCP
    only where they apply."""
    if system == "windows":
        shell = WINDOWS.format(bash=bash) if bash else NO_BASH.format(paths=joined(bash_paths))
    else:
        shell = LINUX
    out = [row("It asks before it acts", ASKS),
           row("Local only", LOCAL.format(server=server)),
           row("/share and /bug", SHARE),
           row("The folder's .pi and AGENTS.md", FOLDER),
           row("Its shell", shell),
           row("Its Node.js", NODE.format(deps=deps)),
           row("Its tools", TOOLS),
           row("Its ports", PORTS),
           row("Its sessions", SESSIONS.format(sessions=sessions))]
    model_row = MODEL
    if chosen:
        model_row += " " + context_words(server, model, typed=typed, known=known, used=used)
        if tools:
            model_row += " " + tools
    out.append(row("The model", model_row))
    if keyed:
        out.append(row("Its key", KEYED.format(server=server)))
    if plain:
        out.append(row("Plain http", PLAIN.format(server=server)))
    if mcp:
        out.append(row("Liminal's MCP", MCP))
    shared = SHARED.format(agent=agent, theirs=THEIRS.get(system, THEIRS["linux"]))
    if yours:
        shared += f" {yours} is yours and is left as it is: never run, read, configured, replaced or removed from here."
    out.append(row("What it shares with a Pi of yours", shared))
    out.append(row("Its configuration", CONFIGURED.format(agent=agent, extension=extension)))
    return out


def table(rows_: list[list[str]]) -> dict:
    return {"title": TABLE, "columns": [dict(c) for c in COLUMNS], "rows": rows_}


def open_words(*, window: bool) -> str:
    """What Open…'s confirmation ends with (after a space): no sandbox, the permission step, the folder's files, its
    sessions."""
    pruned = ("older sessions are removed as it opens" if window else
              "older sessions are removed at the next Open… that opens a window")
    return (" Pi acts as you with no sandbox: this plugin's permission step asks you on its screen before each "
            "command, edit and write (its reads are not asked), and what you allow runs at once. A folder's .pi/ is "
            f"not loaded; its AGENTS.md and CLAUDE.md are. Each session is saved: the newest {SESSIONS_KEPT} are kept, "
            f"{pruned}.")


def parts(node_archive: str, rg_archive: str) -> str:
    """What Install downloads, in words (the install's confirmation goes on "… is downloaded from")."""
    return (f"Node.js {NODE_VERSION} ({node_archive}), Pi {PIN} with the packages npm resolves for it (npm's "
            f"registry), and ripgrep {RIPGREP} ({rg_archive})")


def keeps(config: str) -> str:
    """What an uninstall leaves, in words."""
    return (f"What it kept stays: {config}, with its sessions (your prompts and code), its settings, the lock npm "
            "wrote at its first install (a reinstall of the same pin installs the same packages from it) and its "
            "configuration.")


def pinned(node_archive: str) -> str:
    return f"Pi {PIN} on Node.js {NODE_VERSION} ({node_archive})"


def yours_fact(path: str) -> str:
    return f"{path} is yours: left as it is, not used from here"


def bash_fact(path: str) -> str:
    return f"Git for Windows' bash: {path}"


def unpinned(where: str) -> str:
    return (f"Node.js {NODE_VERSION}'s archive for {where} is not pinned in this release of the plugin (its size and "
            "sha256, from nodejs.org's SHASUMS256.txt, are read before a release installs it): Pi is not installed "
            "from here")


def no_bash_problem(paths: Iterable[str]) -> str:
    return (f"no Git for Windows' bash is installed ({joined(paths)} looked at): Pi is not started without it, and "
            "installing Git for Windows is yours to do (WSL's bash.exe is never used from here)")


def wsl_bash(path: str) -> str:
    return (f"{path} is WSL's launcher, which would run Pi's commands inside a WSL distribution: it is never used "
            "from here")


def planted(folder: str, name: str) -> str:
    return (f"{folder} holds {name} at its top, which part of Pi would run from there in place of the one on your "
            "PATH: open Pi in another folder, or move that file")


def too_small(server: str, context: int) -> str:
    return (f"Pi is started with a context of {FEWEST:,} tokens at the least, and {context:,} leaves its instructions "
            f"and its tools no room (give the real one under Use…, or start {server} with more)")


def value_words(why: str) -> str:
    return f"Pi cannot be given what this start needs: {why}. Nothing was started"


def sessions_words(removed: int) -> str:
    return f"{removed:,} older session{'' if removed == 1 else 's'} removed"


def musl_words() -> str:
    return "Node.js publishes no build for a musl Linux (Alpine's among them): Pi is not installed here"


def machine_words(machine: str, where: str) -> str:
    return f"Node.js {NODE_VERSION} has no build for {machine or 'this processor'} on {where}: Pi is not installed here"
