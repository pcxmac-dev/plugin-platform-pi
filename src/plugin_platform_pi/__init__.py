"""Pi for Liminal (the user, 2026-11-18: "top 4 inference engines, top 4 agentic harnesses (open source)", "all
platform", "both linux and windows compatibility"; 2026-11-25, answers 7 and 8: Pi "kept, with the plugin's own
permission step before every shell command, edit and write", and the ports a tool opens by itself said on its page;
and, from 2026-11-16 and 2026-11-17: "they will be classified as AI plugins", "all plugins are middleware"): Pi's
open-source coding agent (@earendil-works/pi-coding-agent), installed pinned with a Node.js of its own into the
platform's own folder, configured against one instance of an inference plugin's, and opened in a folder the user
picks.

A harness (liminal_libs.machines.harness.Harness, liminal-libs 1.66.0), so middleware of that kind: the standard
interface of a harness, with no hook of its own. The base gives the install's job and its forms, Use… (the instance,
asked of the inference plugins through the platform, its model and Pi's options kept through the login), Open… (a
window of its own where there is a desktop, the lines to paste anywhere else), Command…, Liminal's MCP (off unless
Use… turns it on), and keeps every pair of Liminal's out of what it starts. What this plugin says:

- Install: Node.js 24.22.3 for this system, pinned by name, size and sha256 (none is pinned in 0.1.0, so Install is
  refused in words until a release pins them), unpacked into <home>/app/1.5.2/node; then Pi 1.5.2 by that node's own
  npm (liminal_libs.machines.node: no script run, none of your npm settings, its sha512 compared with the pin, its lock
  kept for a repair) into app/1.5.2/cli; then ripgrep 15.1.0, pinned, into app/1.5.2/bin, which each start places
  where Pi looks (its agent folder's bin/), so Pi never downloads its own. A Pi of the user's own (on PATH) is a fact,
  never run, read, configured, replaced or removed.
- The start: that node with Pi's dist/bundle/cli.js, by their whole paths, in the folder, with its own agent folder
  (PI_CODING_AGENT_DIR) and sessions folder; models.json, mcp.json, settings.json and the permission step written
  whole there at each start (files.py); offline (PI_OFFLINE=1, PI_TELEMETRY=0, PI_SKIP_VERSION_CHECK=1); on Windows
  Git for Windows' bash by its whole path, never WSL's launcher, and no program looked up in the folder first. The
  instance's key, where one is kept, is in its environment alone.
- Its permission step: Pi asks nothing before a tool call and has no sandbox, by its makers' design. The extension the
  plugin writes and Pi loads (-e) asks you on Pi's screen before each call that is not a read, and refuses what you
  decline (files.PERMISSION; C-P1.1: the tool_call event holds a call until its handler answers).
- Its sessions: Pi saves every session's transcript in its sessions folder; the newest 100 (200 MB at the most) are
  kept, older ones removed as Open… opens a window while none of its windows is open.
- Refused before a start, in words: on Windows no Git for Windows' bash, a folder holding at its top a program part of
  Pi would run from there (`planted`), a value Pi would read as more than text ($, ${, $(, a leading !), a context it
  is not told or under 8,192 tokens.
- Before you use it (page.py): what it asks before it acts, what stays local, /share and /bug, the folder's .pi/ and
  AGENTS.md, its shell, its Node.js, its tools, its ports, its sessions, the model, what it shares with a Pi of yours,
  its configuration; a key, plain http and Liminal's MCP where they apply. Nothing is run or asked over the network
  for the page.

    python -m plugin_platform_pi status | command [FOLDER]
"""
from __future__ import annotations

import json
import ntpath
import os
import platform as py_platform
import posixpath
import shutil
import sys
import threading
from pathlib import Path
from typing import Callable, Mapping

from liminal_libs import mounts
from liminal_libs.machines import children, download, harness, node
from liminal_libs.machines.ai import Installed, Outside, Package, Refusal, Setting
from liminal_libs.machines.children import Launch
from liminal_libs.machines.download import Source
from liminal_libs.machines.harness import Harness, HarnessRun, Use, server_words

from . import constants as pins
from . import files, page
from .apis import APIS, NODE, NPM, PI

__version__ = "0.1.0"
LIBS_FLOOR = "1.99.0"  # pyproject's floor: the base's changes page-only (1.99.0), machines/node.py (1.66.0)
PI_PIN = node.Pin(pins.PACKAGE, pins.PIN, pins.INTEGRITY)


def _get(env: Mapping[str, str], name: str, windows: bool) -> str:
    """A variable of `env`, told apart without regard to case on Windows, as Windows reads a name."""
    if not windows:
        return str(env.get(name) or "")
    wanted = name.upper()
    return next((str(v) for k, v in env.items() if str(k).upper() == wanted and v), "")


def _number(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def _wsl_launcher(path: str) -> bool:
    """Whether `path` is WSL's bash.exe: System32's, Sysnative's or a WindowsApps alias, by its last two parts."""
    parts = [p.lower() for p in str(path).replace("/", "\\").split("\\") if p]
    return len(parts) >= 2 and parts[-1] == "bash.exe" and parts[-2] in ("system32", "sysnative", "windowsapps")


class PiRun(HarnessRun):
    """The harness's run state, with Pi's files written one start at a time and what the last window's pruning
    removed."""

    def __init__(self):
        super().__init__()
        self.writing = threading.Lock()  # (two Open… at once)
        self.pruned = 0


class PiPlugin(Harness):
    """Pi, a harness of the platform's AI plugins: its coding agent installed, pinned, on a Node.js of its own, started
    against one model server's instance in a folder you pick, asking you before each command, edit and write
    (Harness: Use…, Open…, Command…, the install's job, Liminal's MCP)."""

    name = "pi"
    title = "Pi"
    about = page.ABOUT
    order = 524  # the harnesses: OpenCode 520, Aider 521, Continue 522, Codex CLI 523, Pi 524, goose 525
    ICON = "pi"  # Pi's own mark (liminal-libs 1.66.0's icons.js)
    LIBS_FLOOR = LIBS_FLOOR
    apis = APIS  # what it attaches to: Pi itself, its configuration, npm's registry, Node.js
    RUN_STATE = PiRun
    OPTIONS = (
        Setting("context", "Context", "number", min=pins.FEWEST, max=pins.MOST,
                note="what the model really has on that server, in tokens: Pi is told it; left empty: the server's "
                     "word"),
        Setting("tools", "Tools", "choice", "auto",
                choices=(("auto", "auto", "the server's word; yes where it says nothing"),
                         ("yes", "yes", "the model calls tools"),
                         ("no", "no", "the model calls no tools: Pi can answer, not act"))),
        harness.MCP_OPTION,
    )
    # Liminal's MCP through the MCP plugin's bridge, a stdio server of Pi's mcp.json (Pi resolves ${NAME} in its env)
    MCP_WIRES = ("stdio",)
    # what Pi reads in a value as more than text, beside the base's: $NAME (C-P1.5a: models.json and mcp.json resolve
    # $NAME and ${NAME}; a leading ! runs a command, which the base refuses)
    OPENERS = (*Harness.OPENERS, "$")
    # What it says of the interface it shares (read by name by the Internal API tab, liminal-libs 1.63.0): no hook of
    # its own beyond the harness base's, so no read of its own and no change of its own (PAGE_ONLY_HOOKS: the base's);
    # it serves no other plugin; what it asks of the others (serving, models_of, and the MCP plugin's four) and what
    # it keeps through the login (its use) are the base's ASKS and KEEPS.
    READ_HOOKS: tuple[str, ...] = ()
    SERVICE_HOOKS: tuple[str, ...] = ()
    ASKS = (*Harness.ASKS, *harness.MCP_ASKS)
    INTERNAL_NOTES = (
        *Harness.INTERNAL_NOTES,
        *harness.MCP_NOTES,
        "A harness (liminal_libs.machines.harness.Harness): the standard interface of its kind, with no hook of its "
        "own. What it adds is inside launch() and its window: models.json, mcp.json, settings.json and its permission "
        "step written for Pi, its tools placed, its older sessions pruned as a window opens.",
        "Its permission step is an extension Pi loads, not a hook of the platform's: it asks on Pi's own screen, "
        "never through the platform.",
    )
    # What it needs of a machine (the needs plan's rows, in its getattr idiom: the library has no needs module yet, so
    # the base's NEEDS is read only through getattr). Each row is a part: what lacks one is said, the rest still works.
    NEEDS = (*getattr(Harness, "NEEDS", ()),
             ("architecture", "x86-64|arm64", "part", "its Node.js: the builds Node.js publishes"),
             ("libc", "glibc", "part", "Node.js 24's Linux builds: none for a musl Linux"),
             ("tool", "bash", "part", "its shell: on Windows Git for Windows' bash, never WSL's launcher"),
             ("internet", "yes", "part", "its install, on a click"))

    def __init__(self, outside: Outside | None = None, *, machine: Callable[[], str] | None = None,
                 exists: Callable[[str], bool] | None = None, libc: Callable[[], tuple[str, str]] | None = None):
        """`outside`: the AI base's outside things (a test's stand-ins); `machine`: what this processor is
        (platform.machine()); `exists` and `libc`: what node.musl_here looks at (os.path.exists, platform.libc_ver).
        None: the real ones, looked at when asked. Making it reads nothing."""
        super().__init__(outside)
        self._machine, self._exists, self._libc = machine, exists, libc

    # -- this system's build ------------------------------------------------------------------------------------------
    def machine_word(self) -> str:
        """This processor as Python names it ("AMD64", "x86_64", "aarch64"): "" where it cannot say."""
        try:
            return str((self._machine or py_platform.machine)() or "").strip()
        except Exception:  # noqa: BLE001 - a machine that cannot be named has no build here
            return ""

    def arch(self) -> str:
        """This processor in Node.js's words ("x64", "arm64"): "" for one it publishes no build for."""
        return pins.ARCHES.get(self.machine_word().lower(), "")

    def musl(self) -> bool:
        """Whether this is a musl Linux, for which Node.js publishes no build (node.musl_here). Files looked at only."""
        if self.system == "windows":
            return False
        kwargs = {}
        if self._exists is not None:
            kwargs["exists"] = self._exists
        if self._libc is not None:
            kwargs["libc"] = self._libc
        try:
            return node.musl_here(system=self.system, **kwargs)
        except Exception:  # noqa: BLE001 - not known: taken for glibc, as Node.js's own builds would then say
            return False

    def _where(self) -> str:
        return "Windows" if self.system == "windows" else "Linux"

    def node_build(self) -> tuple[str, int, str] | None:
        """Node.js's archive for this system: (archive, bytes, sha256); None where none is pinned."""
        return pins.NODE_BUILDS.get((self.system, self.arch()))

    def runs_here(self) -> str:
        """"" or why Pi is not installed on this system, in words: macOS (not this plugin's), a musl Linux, a processor
        Node.js has no build for, a Node.js archive this release does not pin."""
        if self.out.system is None and sys.platform == "darwin":
            return "Pi is installed from here on Windows and Linux only"
        if self.musl():
            return page.musl_words()
        if not self.arch():
            return page.machine_words(self.machine_word(), self._where())
        if self.node_build() is None:
            return page.unpinned(f"{self._where()} on {self.arch()}")
        return ""

    def sources(self) -> list[tuple[str, Source]]:
        """What Install downloads for this system, each pinned by its name, its size and its sha256: ("node", Node.js's
        archive), ("rg", ripgrep's), and ("fd", fd's) where this release pins it."""
        build = self.node_build()
        if build is None:
            raise Refusal(self.runs_here() or page.unpinned(self._where()))
        name, size, sha = build
        out = [("node", Source(pins.NODE_FILES + name, name, size, sha))]
        for tool, files_at, builds in (("rg", pins.RIPGREP_FILES, pins.RIPGREP_BUILDS),
                                       ("fd", pins.FD_FILES + (pins.FD and f"v{pins.FD}/"), pins.FD_BUILDS)):
            got = builds.get((self.system, self.arch()))
            if got is None:
                if tool == "rg":
                    raise Refusal(f"ripgrep {pins.RIPGREP} has no build pinned for {self._where()} on {self.arch()}: "
                                  "Pi is not installed here")
                continue
            out.append((tool, Source(files_at + got[0], got[0], got[1], got[2], pins.ASSET_HOSTS)))
        return out

    # -- its folders --------------------------------------------------------------------------------------------------
    def config_dir(self) -> Path:
        return Path(os.path.abspath(self.home / "config"))

    def agent_dir(self) -> Path:
        """Pi's agent folder for what is started from here (PI_CODING_AGENT_DIR), as a whole path."""
        return self.config_dir().joinpath(*pins.AGENT)

    def sessions_dir(self) -> Path:
        """Pi's sessions folder for what is started from here (PI_CODING_AGENT_SESSION_DIR)."""
        return self.config_dir().joinpath(*pins.SESSIONS)

    def extension_path(self) -> Path:
        """The permission step's file: never in the agent folder's extensions/, which Pi would load a second time."""
        return self.config_dir().joinpath(*pins.EXTENSION)

    # -- what is installed --------------------------------------------------------------------------------------------
    def _node_in(self, folder: Path) -> Path:
        return Path(folder).joinpath("node", *node.PROGRAM["windows" if self.system == "windows" else "linux"])

    def _entry_in(self, folder: Path) -> tuple[Path, str] | None:
        """Pi's program in an install (its package.json's bin `pi`) and its version; None where it is not there."""
        return node.entry_of(PI_PIN.where(Path(folder) / "cli"), pins.BIN)

    def _tool_in(self, folder: Path, tool: str) -> Path:
        return Path(folder) / "bin" / pins.TOOLS[tool]["windows" if self.system == "windows" else "linux"]

    def package(self) -> Package | None:
        """What Install brings here: Node.js 24.22.3, Pi 1.5.2 by npm and ripgrep 15.1.0, their licences and the hosts
        they come from; None where nothing is installed from here."""
        if self.runs_here():
            return None
        found = dict(self.sources())
        size = sum(s.size for s in found.values())
        return Package("Pi", pins.PIN, size, pins.LICENCE + " " + pins.RIPGREP_LICENCE, pins.HOSTS,
                       parts=page.parts(found["node"].name, found["rg"].name), keeps=page.keeps(str(self.config_dir())),
                       checked=page.CHECKED)

    def installed(self) -> Installed | None:
        """This plugin's install, files looked at only: the folder app/CURRENT names, with its node, Pi's program as
        its package.json names it, and ripgrep. One of the user's own is never this (it is the fact `yours`)."""
        folder = self.current()
        if folder is None or not self._node_in(folder).is_file() or not self._tool_in(folder, "rg").is_file():
            return None
        entry = self._entry_in(folder)
        if entry is None:
            return None
        return Installed(entry[1] or folder.name, str(entry[0]), "plugin")

    def _mine(self, path: Path) -> bool:
        try:
            Path(path).resolve().relative_to(Path(self.home).resolve())
        except (OSError, ValueError):
            return False
        return True

    def yours(self) -> str:
        """A Pi of the user's own ("" when there is none): a program named pi on PATH that is not this plugin's. Looked
        at only: never run, read, configured, replaced or removed from here."""
        try:
            on_path = self.out.which("pi")
        except Exception:  # noqa: BLE001 - a PATH that cannot be read: none found there
            on_path = None
        if on_path and not self._mine(Path(on_path)):
            try:
                if Path(on_path).is_file():
                    return str(on_path)
            except OSError:
                return ""
        return ""

    def _npm_run(self):
        """The runner npm's commands are handed (node.py's `stream`): the Outside's streamer where it gives one (a
        test's), else children.stream, its lines without a secret this plugin knows."""
        streamer = self.out.streamer

        def run(argv, line, *, env, cwd, timeout, cancel):
            def said(text: str) -> None:
                line(self._scrubbed(text))
            if streamer is not None:
                return streamer(list(argv), said, env=env, cwd=cwd, timeout=timeout, cancel=cancel)
            return children.stream(argv, said, env=env, cwd=cwd, timeout=timeout, cancel=cancel, popen=self.out.popen,
                                   system=self.system)
        return run

    def _placed(self, folder: Path, archive: Path, tool: str, log, cancel) -> str:
        """A tool's archive unpacked into a folder of its own inside the install, its program moved to bin/ and the
        rest removed: its line."""
        program = pins.TOOLS[tool]["windows" if self.system == "windows" else "linux"]
        unpacked = folder / f".{tool}"
        self.unpack(archive, unpacked, log=log, cancel=cancel, strip=1)
        found = unpacked / program
        if not found.is_file():
            raise download.DownloadError(f"{archive.name} holds no {program}: Pi is not installed")
        target = self._tool_in(folder, tool)
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(found, target)
        download.remove_tree(unpacked, folder)
        if self.system != "windows" and not os.access(target, os.X_OK):
            os.chmod(target, (target.stat().st_mode & 0o777) | 0o700)
        return f"{program}: {target}"

    def install_into(self, log, cancel) -> list[str]:
        """Node.js's archive downloaded (checked against its pinned size and sha256) and unpacked into app/1.5.2/node;
        Pi 1.5.2 put into app/1.5.2/cli by that node's npm (node.put: from the lock kept at its first install when
        there is one, else npm install; its sha512 compared with the pin either way); ripgrep (and fd where pinned)
        into app/1.5.2/bin; then put in use and the archives removed. A cancel or a failure leaves the install in use
        as it was (the base removes the half-built folder)."""
        found = self.sources()
        folder = self.building(pins.PIN)
        lines: list[str] = []
        node_source = found[0][1]
        archive = self.fetch(node_source, log=log, cancel=cancel)
        self.unpack(archive, folder / "node", log=log, cancel=cancel, strip=node.STRIP)
        program, npm_cli = node.programs(folder / "node", self.system, node_source.name)
        lines.append(f"Node.js {pins.NODE_VERSION}: {program}")
        cache = self.home / "downloads" / "npm"
        env = node.child_env(cache, node.write_npmrc(self.home), pins.REGISTRY, base=self.out.env,
                             drop=(*self.dropped(), *pins.DROP), system=self.system)
        lines += node.put(program, npm_cli, folder / "cli", PI_PIN, kept=node.lock_folder(self.home, PI_PIN), env=env,
                          log=log, cancel=cancel, command=pins.BIN, stream=self._npm_run())
        for tool, source in found[1:]:
            lines.append(self._placed(folder, self.fetch(source, log=log, cancel=cancel), tool, log, cancel))
        lines += self.adopt(pins.PIN)
        return [*lines, *self.forget_downloads()]

    # -- its shell on Windows -----------------------------------------------------------------------------------------
    def bash_looked(self) -> list[str]:
        """Where Git for Windows' bash.exe is looked for, in Pi's own order after shellPath, then a per-user install."""
        env = self._env()
        looked = []
        for variable, parts in pins.GIT_BASH:
            base = _get(env, variable, True)
            if base:
                looked.append(os.path.join(base, *parts))
        return looked

    def git_bash(self) -> str:
        """Git for Windows' bash.exe, the first found of `bash_looked` ("" for none). Never WSL's launcher, whatever
        PATH says, and never a path that leads to it. Files looked at only."""
        if self.system != "windows":
            return ""
        for path in self.bash_looked():
            try:
                if not os.path.isfile(path):
                    continue
                real = os.path.realpath(path)
            except OSError:
                continue
            if _wsl_launcher(path) or _wsl_launcher(real):
                continue
            return os.path.abspath(path)
        return ""

    # -- what Pi runs by name -----------------------------------------------------------------------------------------
    def _endings(self) -> set[str]:
        """The endings Windows runs a program by, as cross-spawn's which tries them (lower-cased): those PATHEXT names
        in the environment Pi is started from, and which's own (.com, .exe, .bat, .cmd)."""
        said = _get(self._env(), "PATHEXT", True)
        return {e.lower() for e in (*pins.ENDINGS, *(said.split(";") if said else ())) if e}

    def planted(self, folder: str) -> str:
        """On Windows, a program at the top of `folder` that part of Pi would run from there before the one on its PATH
        ("": none), C-P1.4a's list (PLANTED), each with an ending Windows runs a program by. Its name as the folder
        holds it. On Linux, "": a bare name is looked up on PATH alone, whose relative entries are left out."""
        if self.system != "windows":
            return ""
        endings = self._endings()
        wanted = {name + ending for name in pins.PLANTED for ending in endings}
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            return ""
        return next((n for n in names if n.lower() in wanted), "")

    def _whole_path(self) -> str | None:
        """The platform's PATH with its relative and empty entries left out (Pi and its commands are given no PATH
        entry that means the folder they are in), None when it has none to leave out."""
        windows = self.system == "windows"
        given = _get(self._env(), "PATH", windows)
        if not given:
            return None
        parts = given.split(";" if windows else ":")
        if windows:
            def absolute(entry: str) -> bool:
                bare = entry.strip().strip('"')
                return len(bare) > 2 and bare[1] == ":" and bare[2] in "\\/" or bare.startswith("\\\\")
            whole = [p for p in parts if absolute(p)]
        else:
            whole = [p for p in parts if p.startswith("/")]
        return None if len(whole) == len(parts) else (";" if windows else ":").join(whole)

    # -- the start ----------------------------------------------------------------------------------------------------
    @staticmethod
    def _listed(at: Mapping, model: str) -> dict:
        """The model's row among what its server lists ({"id", "context", "tools"}), {} when it is not listed."""
        for m in at.get("models") or ():
            if isinstance(m, Mapping) and str(m.get("id") or "").strip() == model:
                return dict(m)
        return {}

    def contexts(self, use: Use, at: Mapping) -> tuple[int | None, int | None, int | None]:
        """The model's context: (typed under Use…, the server's word: the model's as it lists it, else the
        instance's, the one Pi is told: the typed one first), each None where it is not said."""
        typed = _number(use.options.get("context"))
        known = _number(self._listed(at, use.model).get("context")) or _number(at.get("context"))
        return typed, known, typed or known

    def tools(self, use: Use, at: Mapping) -> tuple[bool, bool | None, str]:
        """Whether Pi is given its tools, what its server lists of them (True, False, None: not said) and the option
        chosen (auto: the server's word, and yes where it says nothing)."""
        option = str(use.options.get("tools") or "auto")
        listed = self._listed(at, use.model).get("tools")
        listed = listed if isinstance(listed, bool) else None
        told = True if option == "yes" else False if option == "no" else listed is not False
        return told, listed, option

    def _context(self, use: Use, at: Mapping) -> int:
        """The context Pi is told; a Refusal in words when none is said or it leaves Pi no room."""
        words = server_words(at)
        _, _, context = self.contexts(use, at)
        if context is None:
            raise Refusal(f"{words} does not say {use.model}'s context: give it under Use… (Context)")
        if context < pins.FEWEST:
            raise Refusal(page.too_small(words, context))
        return context

    def _write(self, path: Path, text: str) -> None:
        """A generated file written whole (a part file renamed), only when its text changed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if path.read_text(encoding="utf-8") == text:
                return
        except (OSError, UnicodeError):
            pass
        part = path.with_name(path.name + download.PART)
        part.write_text(text, encoding="utf-8", newline="\n")
        os.replace(part, path)

    def _settings_kept(self) -> dict:
        """What settings.json holds now, as it is read back ({} when it cannot be)."""
        try:
            said = json.loads((self.agent_dir() / "settings.json").read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            return {}
        return said if isinstance(said, dict) else {}

    def write_files(self, *, models: dict, mcp: dict, shell_path: str, mcp_on: bool = False) -> None:
        """Pi's three files and the permission step written whole, one start at a time, in the plugin's own folders
        (owner only)."""
        mounts.owner_only(self.config_dir(), "Configuring Pi")
        agent = self.agent_dir()
        with self._rt.writing:
            settings = files.settings_json(system=self.system, shell_path=shell_path, kept=self._settings_kept())
            self._write(agent / "models.json", files.text(models))
            self._write(agent / "mcp.json", files.text(mcp))
            self._write(agent / "settings.json", files.text(settings))
            self._write(self.extension_path(), files.permission_ts(__version__, mcp=mcp_on))

    def place_tools(self, here: Path) -> list[str]:
        """The install's tools copied where Pi looks before PATH (its agent folder's bin/), where they are missing or
        another file is there: the names copied."""
        copied = []
        target_dir = self.agent_dir() / "bin"
        for tool in pins.TOOLS:
            source = self._tool_in(here, tool)
            if not source.is_file():
                continue
            target = target_dir / source.name
            try:
                same = target.is_file() and target.stat().st_size == source.stat().st_size and \
                    target.read_bytes() == source.read_bytes()
            except OSError:
                same = False
            if same:
                continue
            target_dir.mkdir(parents=True, exist_ok=True)
            part = target.with_name(target.name + download.PART)
            shutil.copyfile(source, part)
            if self.system != "windows":
                os.chmod(part, 0o700)
            os.replace(part, target)
            copied.append(source.name)
        return copied

    def launch(self, folder: str, use: Use, at: dict, key: str = "") -> Launch:
        """Pi started in `folder` against the instance `at` with `use`'s model and options: its three files and the
        permission step written whole into its own folders (`write_files`), its tools placed (`place_tools`), that
        node with Pi's cli.js and files.arguments (the permission step, the provider, the model, --no-tools where
        chosen), its folders, its three switches off, its compile cache, on Windows its PATH looked up alone, and the
        key (where one is kept, named by LIMINAL_SERVER_KEY alone) in its environment, a PATH without relative
        entries. Refused in words: its own folder on another system's drive; not installed; on Windows no Git for
        Windows' bash; a folder holding a program part of Pi would run from there; what Pi would read as more than
        text in the server's address or the model's id; a context it is not told, or one under 8,192 tokens."""
        trouble = self.home_problem()
        if trouble:
            raise Refusal(trouble)
        here = self.current()
        have = self.installed()
        if here is None or have is None:
            raise Refusal(f"{self.title} is not installed here: Install… first")
        bash = ""
        if self.system == "windows":
            bash = self.git_bash()
            if not bash:
                raise Refusal(page.NO_BASH.format(paths=page.joined(self.bash_looked()) or "none of its folders is "
                                                  "named in the platform's environment"))
        where = os.path.abspath(str(folder))
        found = self.planted(where)
        if found:
            raise Refusal(page.planted(where, found))
        address = str(at.get("openai") or "").strip()
        self.clean_value(address, "the server's address")
        self.clean_value(use.model, "the model's id")
        context = self._context(use, at)
        told, _, _ = self.tools(use, at)
        wiring = self.mcp_wiring(use)  # (None while Liminal's MCP is off; asked last: a refusal above asks nothing)
        mcp = files.mcp_json()
        if wiring is not None:  # (a whole path: Pi's cross-spawn looks a bare name up in the folder first, C-P1.4a)
            whole = ntpath.isabs if self.system == "windows" else posixpath.isabs
            if not wiring.argv or not whole(wiring.argv[0]):
                raise Refusal(page.value_words("the MCP plugin's bridge is not named by a whole path"))
            mcp = files.mcp_json(wiring.argv, wiring.timeout_s)
        models = files.models_json(base_url=address, model=use.model, context=context, keyed=bool(key))
        self.write_files(models=models, mcp=mcp, shell_path=bash, mcp_on=wiring is not None)
        self.place_tools(here)
        env = {"PI_CODING_AGENT_DIR": str(self.agent_dir()), "PI_CODING_AGENT_SESSION_DIR": str(self.sessions_dir()),
               **pins.OFF, "NODE_COMPILE_CACHE": str(self.config_dir().joinpath(*pins.COMPILE_CACHE))}
        if self.system == "windows":
            env[pins.NO_FOLDER_FIRST] = "1"
        path = self._whole_path()
        if path is not None:
            env["PATH"] = path
        if key:
            env[pins.SECRET] = key
        argv = [os.path.abspath(self._node_in(here)), os.path.abspath(have.path),
                *files.arguments(extension=str(self.extension_path()), model=use.model, tools=told)]
        return Launch(tuple(argv), env=env, cwd=folder, drop=pins.DROP, secret=(pins.SECRET,) if key else ())

    # -- its sessions -------------------------------------------------------------------------------------------------
    def sessions(self) -> list[tuple[float, int, Path]]:
        """Pi's saved sessions (every .jsonl under its sessions folder), the newest first: (when written, bytes,
        path). SESSIONS_LOOKED files at the most. Looked at only."""
        found: list[tuple[float, int, Path]] = []
        for root, _, names in os.walk(self.sessions_dir()):
            for n in names:
                if len(found) >= pins.SESSIONS_LOOKED:
                    break
                if not pins.SESSION.search(n):
                    continue
                path = Path(root) / n
                try:
                    st = path.stat(follow_symlinks=False)
                except OSError:
                    continue
                found.append((st.st_mtime, st.st_size, path))
        return sorted(found, key=lambda t: (t[0], str(t[2])), reverse=True)

    def prune_sessions(self) -> int:
        """Older sessions removed: all but the newest SESSIONS_KEPT, and past SESSIONS_BYTES of them (the newest
        first), then the folders that held them, if empty. Nothing while one of its windows is open (a session may be
        writing its own). The files removed."""
        if self.running():
            return 0
        kept = total = removed = 0
        for _, size, path in self.sessions():
            if kept < pins.SESSIONS_KEPT and total + size <= pins.SESSIONS_BYTES:
                kept, total = kept + 1, total + size
                continue
            try:
                path.unlink()
                removed += 1
            except OSError:
                continue  # (in use, or gone already: the next Open… looks again)
        if removed:
            top = self.sessions_dir()
            for root, _, _ in sorted(os.walk(top), key=lambda w: len(w[0]), reverse=True):
                if Path(root) != top:
                    try:
                        os.rmdir(root)
                    except OSError:
                        pass  # (not empty)
        return removed

    def _window(self, launch: Launch, folder: str, token: str = "") -> tuple[int | None, str]:
        """The base's window, Pi's older sessions pruned just before it opens."""
        removed = self.prune_sessions()
        with self._rt.lock:
            self._rt.pruned = removed
        return super()._window(launch, folder, token)

    def open(self, folder=None) -> dict:
        """Pi started in `folder` against the server Use… chose (the base's Open…), its older sessions pruned as the
        window opens (said among its lines)."""
        with self._rt.lock:
            self._rt.pruned = 0
        out = super().open(folder)
        with self._rt.lock:
            removed, self._rt.pruned = self._rt.pruned, 0
        if removed and out.get("ok"):
            out = {**out, "lines": [*(out.get("lines") or []), page.sessions_words(removed)]}
        return out

    def open_words(self, use: Use, at) -> str:
        """What Open…'s confirmation ends with: no sandbox, its permission step, the folder's files, its sessions."""
        return page.open_words(window=self._desktop())

    # -- its Main -----------------------------------------------------------------------------------------------------
    def main_more(self) -> dict:
        """Before you use it: what Pi does that you should know before a start (page.rows), drawn before the Model
        servers table. Nothing is run or asked over the network."""
        use = self.use_kept()
        at = self.serving_of(use.server) if use is not None else None
        common = dict(system=self.system, agent=str(self.agent_dir()), sessions=str(self.sessions_dir()),
                      extension=str(self.extension_path()), bash=self.git_bash(), bash_paths=self.bash_looked(),
                      yours=self.yours(), mcp=self.mcp_on(use), deps=node.checked_words("Pi"))
        if use is None or at is None:
            rows = page.rows(server=page.NO_SERVER, model="", typed=None, known=None, used=None, tools="",
                             keyed=False, plain=False, chosen=False, **common)
            return {"tables": [page.table(rows)]}
        typed, known, context = self.contexts(use, at)
        told, listed, option = self.tools(use, at)
        rows = page.rows(server=server_words(at), model=use.model, typed=typed, known=known, used=context,
                         tools=page.tools_words(told, listed, option), keyed=bool(str(at.get("key") or "").strip()),
                         plain=bool(at.get("plain")), chosen=True, **common)
        return {"tables": [page.table(rows)]}

    def status(self) -> dict:
        """Its Main: the harness's (the install, what it uses, the Model servers, Use…, Open…, Command…), Before you
        use it, and its facts: what is pinned for this system, a Pi of yours, its shell on Windows; as a problem, no
        Git for Windows' bash. Nothing is run and nothing is asked over the network. Never raises."""
        out = super().status()
        if out.get("applies") is False or not out.get("valid", True):
            return out
        build = self.node_build()
        if build is not None:
            out["pinned"] = page.pinned(build[0])
        yours = self.yours()
        if yours:
            out["yours"] = page.yours_fact(yours)
        if self.system == "windows":
            bash = self.git_bash()
            if bash:
                out["shell"] = page.bash_fact(bash)
            else:
                problems = [str(out.get("problem") or ""), page.no_bash_problem(self.bash_looked())]
                out["problem"] = "; ".join(p for p in problems if p)
        return out

    def api_facts(self) -> dict:
        """What it holds of its APIs, asking nothing: the install, what it is started against, its folders, its
        Node.js."""
        try:
            have, use, build = self.installed(), self.use_kept(), self.node_build()
        except Exception:  # noqa: BLE001 - what it holds is extra: its page is drawn without it
            return {}
        return {
            PI: {"Installed": f"{have.version} in {have.path}" if have is not None else "not installed",
                 "Started against": f"{use.server}: {use.model}" if use is not None else "nothing yet",
                 "Its agent folder": str(self.agent_dir())},
            NPM: {"Pinned": f"{PI_PIN.spec} ({PI_PIN.integrity[:19]}…)"},
            NODE: {"This system's archive": build[0] if build is not None else "none pinned in this release"},
        }


MACHINE = PiPlugin()

__all__ = ["MACHINE", "PI_PIN", "PiPlugin", "Refusal", "LIBS_FLOOR", "__version__"]
