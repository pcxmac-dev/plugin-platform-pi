"""What every test here shares.

Nothing real is reached (the library's own guard, tests/conftest.py's `no_outside`, made autouse here): a process
started, a connection opened, a socket bound or a name resolved raises `Reached`, a BaseException that no `except
Exception` of the code under test can swallow, and every reach is noted and fails the test at its end too. No program
is found on PATH, the platform's folder is a temporary one, no variable Pi's launch drops is set, and every folder is
this system's own disk (mounts.foreign, stood in for). Nothing is installed, downloaded or started: the plugin is driven
with stand-ins for the web (a dict of addresses), npm (a streamer that lays out what npm would), the window's process,
the login and the platform, each noting what it was given. Node.js's archives are pinned for the tests alone
(`node_pins`, autouse): this release pins none.

The platform as a harness asks it (`App`): the model servers the plans name, as each says what it serves (`serving`):
a found Ollama without a key, a llama.cpp with a key (its model listed without a context, its instance's own context
set) and one of its instances stopped, a remote vLLM over plain http, and LMDeploy; and, where a test asks for it
(`mcp`), the MCP plugin beside them, as its plugin offers itself (its bridge and the platform's route), the tokens it
mints and those it is asked to end."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import re
import shutil
import socket
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

try:
    import requests  # noqa: F401 - imported before any guard: urllib3 binds a socket of its own when first imported
except ImportError:  # (not every run has it)
    pass

import plugin_platform_pi as plugin
from liminal_libs import mounts
from liminal_libs.apps.authorization import Login, Unauthorized, pair_name, variable_name
from liminal_libs.machines import node
from liminal_libs.machines.ai import Outside
from liminal_libs.machines.endpoint import Reply
from plugin_platform_pi import constants

HTTP, HTTPS = "http:" + "//", "https:" + "//"  # an address's start, put together here
KEY = "sk-llama-key-0123456789abcdef"  # llama.cpp's key for its instance gpu: in no answer, no file, no line
KEY_VARIABLE = "LIMINAL_AI_LLAMACPP_GPU_KEY"  # the pair it is kept under, as the `serving` row names it
DECLARED = ("MASSIVE_API_KEY", "GROK_API_KEY")  # what the registry says the installed plugins declare
CODER = "Qwen3-Coder-30B-A3B-Q4_K_M"  # llama.cpp's model
DATA = Path(__file__).resolve().parent / "data"
# the MCP plugin's bridge and its route, as its offer names them (plugin-platform-mcp 0.1.0's page.offer)
BRIDGE = ["C:\\Python\\python.exe", "-I", "-S", "C:\\plugins\\plugin-platform-mcp\\bridge.py", "--port", "8775"]
ENDPOINT = HTTP + "127.0.0.1:8775/api/machines/mcp/rpc"
TOKEN_VARIABLE = "LIMINAL_MCP_TOKEN"
NODE_BYTES = {"windows": b"MZ a stand-in node", "linux": b"\x7fELF a stand-in node"}

# -- the guard (the library's tests/conftest.py, made autouse) ---------------------------------------------------------
STOOD_IN = [
    (subprocess, "subprocess", ("Popen", "run", "call", "check_call", "check_output", "getoutput", "getstatusoutput",
                                "_fork_exec")),
    (os, "os", ("system", "startfile", "posix_spawn", "posix_spawnp", "spawnv", "spawnve", "spawnvp", "spawnvpe",
                "fork", "forkpty", "execv", "execve")),
    (socket, "socket", ("create_connection", "create_server", "socketpair", "getaddrinfo", "gethostbyname",
                        "gethostbyname_ex", "gethostbyaddr", "getnameinfo")),
    (socket.socket, "socket.socket", ("connect", "connect_ex", "bind", "listen", "sendto", "sendmsg")),
]
if os.name == "nt":
    import _winapi

    STOOD_IN.append((_winapi, "_winapi", ("CreateProcess",)))
else:
    import _posixsubprocess

    STOOD_IN.append((_posixsubprocess, "_posixsubprocess", ("fork_exec",)))


class Reached(BaseException):
    """A test reached for real what it must stand in for."""


class Asked(BaseException):
    """A stand-in asked that must not be: a BaseException, so no `except Exception` of the code can swallow it."""


def never(what: str):
    def stand_in(*args, **kwargs):
        raise Asked(f"{what} was asked: it must not be")
    return stand_in


@pytest.fixture(autouse=True)
def no_outside(monkeypatch):
    reached: list[str] = []

    def refuse(what):
        def stand_in(*args, **kwargs):
            __tracebackhide__ = True  # its arguments (an environment, with its keys' values) never printed
            reached.append(f"{what} {args[:1]!r}"[:300])
            raise Reached(f"the test reached {what} for real: give the code a stand-in")
        return stand_in

    for owner, said, names in STOOD_IN:
        for name in names:
            if hasattr(owner, name):
                monkeypatch.setattr(owner, name, refuse(f"{said}.{name}"))
    yield reached
    assert not reached, f"the test reached the outside for real: {reached}"


@pytest.fixture(autouse=True)
def not_this_machine(monkeypatch, tmp_path):
    """No program on PATH, the platform's folder a temporary one, no variable the launch drops set (nor any of
    Liminal's but that folder's), every folder on this system's own disk."""
    monkeypatch.setattr(shutil, "which", lambda name, *a, **k: None)
    monkeypatch.setattr(mounts, "foreign", lambda path, *a, **k: False)
    for name in list(os.environ):
        if any(re.fullmatch(re.escape(p[:-1]) + ".*" if p.endswith("*") else re.escape(p), name, re.I)
               for p in (*constants.DROP, "LIMINAL_*")):
            monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LIMINAL_PLATFORM_DIR", str(tmp_path / "platform"))


def stand_in_node(system: str, arch: str) -> tuple[str, bytes]:
    """Node.js's archive for a system as nodejs.org lays it out (one top folder named as the archive, node and
    npm-cli.js where its packaging puts them), holding stand-ins: (its name, its bytes)."""
    name = node.archive(constants.NODE_VERSION, system, arch)
    top = name.removesuffix(".zip").removesuffix(".tar.xz")
    if system == "windows":
        members = {f"{top}/node.exe": NODE_BYTES["windows"],
                   f"{top}/node_modules/npm/bin/npm-cli.js": b"// a stand-in npm", f"{top}/LICENSE": b"MIT"}
        return name, zipped(members)
    members = {f"{top}/bin/node": NODE_BYTES["linux"], f"{top}/lib/node_modules/npm/bin/npm-cli.js": b"// npm",
               f"{top}/LICENSE": b"MIT"}
    return name, tarred(members, "w:xz")


@pytest.fixture(autouse=True)
def node_pins(monkeypatch) -> dict:
    """Node.js's archives pinned for the tests (this release pins none): each system's stand-in, by its own size and
    sum. The bytes by archive name."""
    made: dict[str, bytes] = {}
    for system in ("windows", "linux"):
        for arch in ("x64", "arm64"):
            name, data = stand_in_node(system, arch)
            made[name] = data
            monkeypatch.setitem(constants.NODE_BUILDS, (system, arch),
                                (name, len(data), hashlib.sha256(data).hexdigest()))
    return made


# -- archives ----------------------------------------------------------------------------------------------------------
def tarred(members: dict[str, bytes], mode: str = "w:gz") -> bytes:
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode=mode) as t:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size, info.mode = len(data), 0o755
            t.addfile(info, io.BytesIO(data))
    return out.getvalue()


def zipped(members: dict[str, bytes]) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return out.getvalue()


def stand_in_rg(system: str, arch: str) -> bytes:
    """ripgrep's archive as its release lays it out: ripgrep-15.1.0-<platform>/ with rg and its licences."""
    name = constants.RIPGREP_BUILDS[(system, arch)][0]
    top = name.removesuffix(".zip").removesuffix(".tar.gz")
    program = "rg.exe" if system == "windows" else "rg"
    members = {f"{top}/{program}": b"a stand-in rg", f"{top}/COPYING": b"Unlicense or MIT"}
    return zipped(members) if system == "windows" else tarred(members)


def rg_pin(monkeypatch, system: str, arch: str = "x64") -> tuple[str, bytes]:
    """ripgrep's pin for a system made the stand-in archive's (its name kept, its size and sum the stand-in's)."""
    data = stand_in_rg(system, arch)
    name = constants.RIPGREP_BUILDS[(system, arch)][0]
    monkeypatch.setitem(constants.RIPGREP_BUILDS, (system, arch), (name, len(data), hashlib.sha256(data).hexdigest()))
    return constants.RIPGREP_FILES + name, data


# -- the platform, its login, a window ---------------------------------------------------------------------------------
def row(name, **given) -> dict:
    """One instance as a model server's `serving` says it (machines/modelserver.py's shape, liminal-libs 1.66.0)."""
    out = {"name": name, "title": "", "where": "local", "local": True, "base": HTTP + "127.0.0.1:9931",
           "openai": HTTP + "127.0.0.1:9931/v1", "plain": False, "state": "running", "key": "", "model": "",
           "context": None, "models": [], "asked": "", "port": 9931, "speaks": ["chat", "completions"]}
    out.update(given)
    return out


def serving() -> dict:
    return {
        "ollama": {"plugin": "ollama", "title": "Ollama", "native": "ollama", "instances": [
            row("default", where="found", base=HTTP + "127.0.0.1:11434", openai=HTTP + "127.0.0.1:11434/v1",
                state="answering", port=11434, asked="2026-11-23T10:00:00Z",
                speaks=["chat", "completions", "responses", "embeddings"],
                models=[{"id": "qwen3:8b", "context": 40960, "tools": True},
                        {"id": "gemma3:4b", "context": 32768, "tools": False}])]},
        "llamacpp": {"plugin": "llamacpp", "title": "llama.cpp", "native": "llamacpp", "instances": [
            row("gpu", title="The GPU", key=KEY_VARIABLE, model=CODER, context=65536,
                models=[{"id": CODER, "context": None, "tools": None}]),
            row("cpu", state="stopped", base=HTTP + "127.0.0.1:9932", openai=HTTP + "127.0.0.1:9932/v1", port=9932,
                models=[{"id": "small.gguf", "context": 4096, "tools": None}])]},
        "vllm": {"plugin": "vllm", "title": "vLLM", "native": "vllm", "instances": [
            row("box", where="remote", local=False, base=HTTP + "gpu-box.example.test:8000",
                openai=HTTP + "gpu-box.example.test:8000/v1", plain=True, state="unasked", port=8000,
                models=[{"id": "Qwen/Qwen3-8B", "context": 32768, "tools": None}])]},
        "lmdeploy": {"plugin": "lmdeploy", "title": "LMDeploy", "native": "lmdeploy", "instances": [
            row("turbo", base=HTTP + "127.0.0.1:23333", openai=HTTP + "127.0.0.1:23333/v1", port=23333,
                models=[{"id": "internlm3-8b", "context": 32768, "tools": True}])]},
    }


class App:
    """The platform as a harness asks it: the plugins attached with their hooks, and `ask(name, hook, args)` (its
    form: the arguments as one list), each ask noted. With `mcp`, the MCP plugin beside the model servers: what it
    offers, the tokens it minted and those it was asked to end, its refusals by hook."""

    def __init__(self, mcp: bool = False):
        self.serving = serving()
        self.asked: list[tuple[str, str, list]] = []
        self.mcp = mcp
        self.offer: object = {"wires": ["stdio", "http"], "bridge": list(BRIDGE), "endpoint": ENDPOINT,
                              "headers": {"X-Liminal-Charts": "1"},
                              "revisions": ["2026-07-28", "2025-11-25", "2025-06-18"], "variable": TOKEN_VARIABLE,
                              "hold_s": 50, "agent": "pi"}
        self.minted: list[str] = []
        self.ended: list[str] = []
        self.mcp_refusing: dict[str, BaseException] = {}

    def plugins(self) -> dict:
        faces = {name: {"name": name, "hooks": {"present": "()", "status": "()", "serving": "(name='')",
                                                "models_of": "(name)"}} for name in self.serving}
        faces["pi"] = {"name": "pi", "hooks": {"use": "(server, model, *values)"}}  # itself
        if self.mcp:
            faces["mcp"] = {"name": "mcp", "hooks": {"present": "()", "status": "()", "client_offer": "()",
                                                     "ensure_client": "(title)", "launch_token": "()",
                                                     "end_launch": "(token)"}}
        return faces

    def ask(self, name: str, hook: str, args: list):
        self.asked.append((name, hook, list(args)))
        if name == "mcp" and self.mcp:
            return self._mcp(hook, args)
        if hook == "serving" and name in self.serving:
            return copy.deepcopy(self.serving[name])
        if hook == "models_of" and name in self.serving:
            at = next(r for r in self.serving[name]["instances"] if r["name"] == args[0])
            return {"said": f"{name}/{args[0]} lists {len(at['models'])} models", "ok": True,
                    "models": copy.deepcopy(at["models"]), "asked": "2026-11-23T11:00:00Z"}
        raise LookupError(f"{name} offers no {hook!r}")

    def _mcp(self, hook: str, args: list):
        if hook in self.mcp_refusing:
            raise self.mcp_refusing[hook]
        if hook == "client_offer":
            return copy.deepcopy(self.offer)
        if hook == "ensure_client":
            return {"said": f"{args[0]}'s agent pi is kept, granted nothing yet", "ok": True, "agent": "pi"}
        if hook == "launch_token":
            self.minted.append(f"launch{len(self.minted):02d}-" + "Ab9_" * 10)
            return {"token": self.minted[-1], "agent": "pi", "variable": TOKEN_VARIABLE, "hold_s": 50}
        if hook == "end_launch":
            self.ended.append(args[0])
            return {"ok": True}
        raise LookupError(f"mcp offers no {hook!r}")


class Pairs(Login):
    """The platform's login as a test has it: pairs kept in memory, each save noted."""

    def __init__(self):
        self.kept: dict[str, str] = {}
        self.saved: list[tuple[str, bool]] = []

    def user(self) -> dict:
        return {"name": "someone"}

    def vector(self, name: str) -> str:
        variable = variable_name(name)
        if variable not in self.kept:
            raise Unauthorized(f"no {name}", 404)
        return self.kept[variable]

    def names(self) -> set[str]:
        return {pair_name(v) for v in self.kept}

    def save(self, variable: str, value: str | None) -> str:
        self.saved.append((variable, value is not None))
        if value is None:
            self.kept.pop(variable, None)
        else:
            self.kept[variable] = value
        return "the test's pairs"


class Window:
    """A stand-in for a window's process: its number, and its exit code once it has ended (None: open)."""

    def __init__(self, pid: int):
        self.pid, self.code = pid, None

    def poll(self):
        return self.code


class Popen:
    """A stand-in for subprocess.Popen: what each start was given, and the window it made."""

    def __init__(self):
        self.made: list[dict] = []
        self.windows: list[Window] = []

    def __call__(self, argv, **kw):
        self.made.append({"argv": list(argv), **kw})
        self.windows.append(Window(4321 + len(self.windows)))
        return self.windows[-1]


class Web:
    """https as download.fetch asks it: each address of `files` answered 200 with its bytes; anything else 404. Every
    address asked is noted."""

    def __init__(self, files: dict[str, bytes] | None = None, piece: int = 4096):
        self.files, self.piece = dict(files or {}), piece
        self.asked: list[str] = []

    def __call__(self, url, headers, timeout):
        self.asked.append(url)
        data = self.files.get(url)
        if data is None:
            return Reply(404, {}, iter(()))

        def chunks():
            for at in range(0, len(data), self.piece):
                yield data[at:at + self.piece]
        return Reply(200, {"Content-Length": str(len(data))}, chunks())


class Npm:
    """npm as node.py runs it (the plugin's streamer): each command noted with its environment and folder, and what
    npm would write laid out in its --prefix: Pi's package (its package.json naming its bin, its cli.js), the
    project's package.json and the lock recording `integrity` (the pin's unless a test says another). `code`: its
    exit code."""

    def __init__(self, integrity: str = constants.INTEGRITY, version: str = constants.PIN, code: int = 0):
        self.integrity, self.version, self.code = integrity, version, code
        self.ran: list[dict] = []

    def __call__(self, argv, line, *, env, cwd, timeout, cancel):
        self.ran.append({"argv": list(argv), "env": dict(env), "cwd": cwd})
        line("added 123 packages in 4s")
        if self.code:
            line("npm error code E404")
            return self.code
        prefix = Path(argv[argv.index("--prefix") + 1])
        package = prefix / "node_modules" / "@earendil-works" / "pi-coding-agent"
        (package / "dist" / "bundle").mkdir(parents=True, exist_ok=True)
        (package / "dist" / "bundle" / "cli.js").write_text("// a stand-in pi", encoding="utf-8")
        (package / "package.json").write_text(json.dumps({"name": constants.PACKAGE, "version": self.version,
                                                          "bin": {"pi": "dist/bundle/cli.js"}}), encoding="utf-8")
        if "install" in argv:
            (prefix / "package.json").write_text(json.dumps({"dependencies": {constants.PACKAGE: self.version}}),
                                                 encoding="utf-8")
            (prefix / "package-lock.json").write_text(json.dumps({"lockfileVersion": 3, "packages": {
                "": {"dependencies": {constants.PACKAGE: self.version}},
                f"node_modules/{constants.PACKAGE}": {"version": self.version, "integrity": self.integrity}}}),
                encoding="utf-8")
        return 0


class Clock:
    def __init__(self):
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


# -- the plugin --------------------------------------------------------------------------------------------------------
def git_bash(tmp_path: Path, under: str = "ProgramFiles") -> Path:
    """Git for Windows' bash.exe laid out under one of the folders the plugin looks in."""
    parts = dict(constants.GIT_BASH)[under]
    path = tmp_path.joinpath("win", under, *parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ a stand-in bash")
    return path


def made(tmp_path: Path, system: str = "windows", *, interactive: bool = True, machine: str | None = None,
         app: bool = True, mcp: bool = False, bash: bool = True, musl: bool = False,
         streamer=None) -> plugin.PiPlugin:
    """The plugin on stand-ins: its folder under tmp_path, the platform's environment (a PATH with a relative entry,
    the user's home, a hosted provider's key, Pi's and Node.js's own variables of yours, a pair of Liminal's; on
    Windows the folders Git for Windows is installed under, with its bash.exe where `bash`), a window's process, the
    clock, npm (a stand-in where `streamer` is not given: refusing); every other outside thing refusing to be asked.
    Attached to the stand-in platform (with the MCP plugin where `mcp`) with a login keeping llama.cpp's key."""
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)
    win = tmp_path / "win"
    if system == "windows":
        env = {"PATH": "C:\\Windows\\System32;.\\node_modules\\.bin;C:\\tools", "USERPROFILE": str(home),
               "ProgramFiles": str(win / "ProgramFiles"), "ProgramFiles(x86)": str(win / "ProgramFiles(x86)"),
               "LOCALAPPDATA": str(win / "LOCALAPPDATA"), "SystemRoot": str(win / "Windows"),
               "PATHEXT": ".COM;.EXE;.BAT;.CMD;.PS1"}
        if bash:
            git_bash(tmp_path)
    else:
        env = {"PATH": "/usr/local/bin::/usr/bin", "HOME": str(home)}
    env.update({"ANTHROPIC_API_KEY": "a-key-1", "MASSIVE_API_KEY": "m-key-1", "PI_CODING_AGENT_DIR": "/somewhere/else",
                "PI_OAUTH_CALLBACK_HOST": "0.0.0.0", "NODE_OPTIONS": "--require /tmp/evil.js",
                "npm_config_registry": "https://evil.example.test/", "LIMINAL_PLATFORM_DIR": str(tmp_path / "platform"),
                KEY_VARIABLE: KEY})
    out = Outside(env=env, system=system, wsl="", home=tmp_path / "pi", clock=Clock(),
                  which=lambda name, *a, **k: None, interactive=lambda: interactive, popen=Popen(),
                  opener=never("the web"), streamer=streamer or never("a streamed command"),
                  runner=never("a short command"), transport=never("an instance over http"),
                  listening=never("a port"), powershell=never("PowerShell"), shell=never("a shell"),
                  probe=never("the socket table"), variables=lambda: DECLARED)
    word = machine or ("AMD64" if system == "windows" else "x86_64")
    p = plugin.PiPlugin(out, machine=lambda: word, exists=lambda path: False,
                        libc=lambda: ("", "") if musl else ("glibc", "2.39"))
    if app:
        p.attach(App(mcp=mcp), Pairs())
        p.login.kept[KEY_VARIABLE] = KEY  # kept by llama.cpp's plugin for its instance gpu, through the same login
    return p


def installed(p: plugin.PiPlugin, pin_: str = constants.PIN) -> Path:
    """An install laid out as Install leaves it (app/<pin> with its node, Pi's package and ripgrep, CURRENT naming
    it)."""
    folder = p.home / "app" / pin_
    windows = p.system == "windows"
    program = folder.joinpath("node", *(("node.exe",) if windows else ("bin", "node")))
    program.parent.mkdir(parents=True, exist_ok=True)
    program.write_bytes(NODE_BYTES[p.system])
    package = folder / "cli" / "node_modules" / "@earendil-works" / "pi-coding-agent"
    (package / "dist" / "bundle").mkdir(parents=True, exist_ok=True)
    (package / "dist" / "bundle" / "cli.js").write_text("// a stand-in pi", encoding="utf-8")
    (package / "package.json").write_text(json.dumps({"name": constants.PACKAGE, "version": constants.PIN,
                                                      "bin": {"pi": "dist/bundle/cli.js"}}), encoding="utf-8")
    rg = folder / "bin" / ("rg.exe" if windows else "rg")
    rg.parent.mkdir(parents=True, exist_ok=True)
    rg.write_bytes(b"a stand-in rg")
    (p.home / "app" / "CURRENT").write_text(pin_ + "\n", encoding="utf-8")
    return folder


def chosen(p: plugin.PiPlugin, server="ollama/default", model="qwen3:8b", folder="", **options) -> None:
    """What Use… keeps, kept as the base keeps it (LIMINAL_AI_PI_USE)."""
    p.login.kept[p.variable("use")] = json.dumps({"v": 1, "server": server, "model": model, "folder": str(folder),
                                                  "options": options})


def agent_file(p: plugin.PiPlugin, name: str) -> dict:
    return json.loads((p.agent_dir() / name).read_text(encoding="utf-8"))


def table(status: dict, title: str) -> dict:
    return next(t for t in status["tables"] if t["title"] == title)


def rows(status: dict) -> dict:
    return {what: said for what, said in table(status, "Before you use it")["rows"]}


def form(status: dict, form_id: str) -> dict:
    return next(f for f in status["forms"] if f["id"] == form_id)


def refused(call) -> str:
    with pytest.raises(ValueError) as caught:
        call()
    return str(caught.value)


@pytest.fixture
def project(tmp_path) -> Path:
    folder = tmp_path / "project"
    folder.mkdir()
    return folder


@pytest.fixture
def windows(tmp_path):
    return made(tmp_path, "windows")


@pytest.fixture
def linux(tmp_path):
    return made(tmp_path, "linux")
