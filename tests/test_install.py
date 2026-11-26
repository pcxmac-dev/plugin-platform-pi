"""Install, update and uninstall: Node.js's archive for this system by node.py's names (none pinned in this release:
said, and nothing installed), Pi by that node's npm, word for word, with no script run and none of your npm or
Node.js settings, its sha512 compared with the pin before anything is put in use, the lock kept and used again for a
reinstall of the same pin (npm ci), ripgrep placed in the install's bin/; a musl Linux and an unknown processor refused;
a wrong sha512, a failed npm and an archive without its program each leaving nothing half-built and the install in use
as it was; the uninstall leaving what it keeps; a Pi of yours reported and never run.

Real archives are made here in memory and unpacked by the library for real (zip, tar.gz and tar.xz: Python's own);
the web, npm, the window's process and the login are stand-ins. Nothing is downloaded, installed or started."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

import plugin_platform_pi as plugin
from conftest import HTTPS, Npm, Web, chosen, installed, made, refused, rg_pin
from liminal_libs.machines import node
from liminal_libs.machines.terminal import Output
from plugin_platform_pi import constants

RIPGREP = {  # plugin-platform-opencode 0.1.0's pins of ripgrep 15.1.0 (from its release; OpenCode 2.3.0's own)
    ("windows", "x64"): ("ripgrep-15.1.0-x86_64-pc-windows-msvc.zip", 1810687,
                         "124510b94b6baa3380d051fdf4650eaa80a302c876d611e9dba0b2e18d87493a"),
    ("windows", "arm64"): ("ripgrep-15.1.0-aarch64-pc-windows-msvc.zip", 1675460,
                           "00d931fb5237c9696ca49308818edb76d8eb6fc132761cb2a1bd616b2df02f8e"),
    ("linux", "x64"): ("ripgrep-15.1.0-x86_64-unknown-linux-musl.tar.gz", 2263077,
                       "1c9297be4a084eea7ecaedf93eb03d058d6faae29bbc57ecdaf5063921491599"),
    ("linux", "arm64"): ("ripgrep-15.1.0-aarch64-unknown-linux-gnu.tar.gz", 1869959,
                         "2b661c6ef508e902f388e9098d9c4c5aca72c87b55922d94abdba830b4dc885e"),
}


def test_the_pins_are_npms_record_and_this_release_pins_no_nodejs_archive():
    assert (constants.PACKAGE, constants.PIN, constants.BIN) == ("@earendil-works/pi-coding-agent", "1.5.2", "pi")
    assert constants.INTEGRITY == ("sha512-mUWI04rqF1Vd/m1q+Ps1XeWsTXEVvRUnsmRa83I3Dzua0Tx5bYS93imeqtIfrXf7PkkaR6ERz+"
                                   "AuQhIJlom5yA==")
    assert plugin.PI_PIN == node.Pin(constants.PACKAGE, constants.PIN, constants.INTEGRITY)
    assert constants.RIPGREP_BUILDS == RIPGREP and constants.FD == "" and constants.FD_BUILDS == {}
    assert constants.REGISTRY == HTTPS + "registry.npmjs.org/"
    assert constants.NODE_FILES == HTTPS + "nodejs.org/dist/v24.22.3/"
    tree = ast.parse(Path(constants.__file__).read_text(encoding="utf-8"))
    [given] = [n.value for n in ast.walk(tree) if isinstance(n, ast.AnnAssign) and n.target.id == "NODE_BUILDS"]
    assert isinstance(given, ast.Dict) and given.keys == []  # (the tests pin stand-ins: node_pins)


@pytest.mark.parametrize("system, machine, arch", [("windows", "AMD64", "x64"), ("windows", "ARM64", "arm64"),
                                                   ("linux", "x86_64", "x64"), ("linux", "aarch64", "arm64")])
def test_nodes_source_is_the_archive_node_py_names_for_this_system(tmp_path, system, machine, arch, node_pins):
    p = made(tmp_path, system, machine=machine)
    assert p.arch() == arch and p.runs_here() == ""
    [(n, nodejs), (r, rg)] = p.sources()
    name = node.archive("24.22.3", system, machine)
    assert (n, r) == ("node", "rg")
    assert (nodejs.url, nodejs.name, nodejs.size) == (constants.NODE_FILES + name, name, len(node_pins[name]))
    assert (rg.url, rg.name, rg.size, rg.sha256, rg.hosts) == (constants.RIPGREP_FILES + RIPGREP[(system, arch)][0],
                                                               *RIPGREP[(system, arch)],
                                                               ("release-assets.githubusercontent.com",))
    pkg = p.package()
    assert (pkg.title, pkg.version, pkg.pin) == ("Pi", "1.5.2", "1.5.2")
    assert pkg.size == nodejs.size + rg.size
    assert pkg.hosts == ("nodejs.org", "registry.npmjs.org", "github.com", "release-assets.githubusercontent.com")
    assert pkg.parts == (f"Node.js 24.22.3 ({name}), Pi 1.5.2 with the packages npm resolves for it (npm's registry), "
                         f"and ripgrep 15.1.0 ({RIPGREP[(system, arch)][0]})")
    assert "are pinned in no file of this plugin's" in pkg.checked and pkg.checked.startswith("Node.js 24.22.3's")


def test_an_unpinned_nodejs_is_said_and_installs_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(constants, "NODE_BUILDS", {})
    p = made(tmp_path)
    words = ("Node.js 24.22.3's archive for Windows on x64 is not pinned in this release of the plugin (its size and "
             "sha256, from nodejs.org's SHASUMS256.txt, are read before a release installs it): Pi is not installed "
             "from here")
    assert p.runs_here() == words and p.package() is None
    assert refused(lambda: p.install(True)) == words
    assert not (p.home / "app").exists()


def test_a_musl_linux_and_an_unknown_processor_are_said_and_install_nothing(tmp_path):
    musl = made(tmp_path / "musl", "linux", musl=True)
    assert musl.runs_here() == ("Node.js publishes no build for a musl Linux (Alpine's among them): Pi is not "
                                "installed here")
    assert musl.package() is None and "musl" in refused(lambda: musl.install(True))
    other = made(tmp_path / "other", "linux", machine="riscv64")
    assert other.runs_here() == "Node.js 24.22.3 has no build for riscv64 on Linux: Pi is not installed here"
    assert made(tmp_path / "w", "windows", musl=True).musl() is False  # (Windows has no libc of that kind)


def served(monkeypatch, p, node_pins) -> Web:
    """The web serving this system's Node.js archive and ripgrep's, as pinned."""
    name = node.archive("24.22.3", p.system, p.machine_word())
    url, data = rg_pin(monkeypatch, p.system, p.arch())
    return Web({constants.NODE_FILES + name: node_pins[name], url: data})


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_install_puts_node_pi_and_ripgrep_in_place_and_in_use(tmp_path, monkeypatch, node_pins, system):
    npm = Npm()
    p = made(tmp_path, system, streamer=npm)
    p.out.opener = web = served(monkeypatch, p, node_pins)
    answer = p.install(True, log=Output())
    folder = p.home / "app" / "1.5.2"
    cli = folder / "cli" / "node_modules" / "@earendil-works" / "pi-coding-agent" / "dist" / "bundle" / "cli.js"
    assert answer["ok"] is True and answer["said"] == f"Pi 1.5.2 installed in {cli}"
    assert p.installed().path == str(cli) and p.installed().version == "1.5.2"
    windows = system == "windows"
    program = folder / "node" / ("node.exe" if windows else "bin/node")
    npm_cli = folder / "node" / ("" if windows else "lib") / "node_modules/npm/bin/npm-cli.js"
    [ran] = npm.ran
    assert ran["argv"] == [str(program), str(npm_cli), "install", "--prefix", str(folder / "cli"), "--save-exact",
                           "--ignore-scripts", "--no-audit", "--no-fund", "--no-update-notifier",
                           "@earendil-works/pi-coding-agent@1.5.2"]
    assert ran["cwd"] == str(folder / "cli")
    env = ran["env"]
    rc = str(p.home / "config" / "npmrc")
    assert (env["npm_config_registry"], env["npm_config_userconfig"], env["npm_config_globalconfig"]) == (
        "https://registry.npmjs.org/", rc, rc)
    assert env["npm_config_cache"] == str(p.home / "downloads" / "npm")
    for name in ("NODE_OPTIONS", "ANTHROPIC_API_KEY", "MASSIVE_API_KEY", "PI_CODING_AGENT_DIR", "LIMINAL_PLATFORM_DIR",
                 "LIMINAL_AI_LLAMACPP_GPU_KEY"):
        assert name not in env, name
    assert (p.home / "config" / "npmrc").read_text(encoding="utf-8") == ""
    assert (folder / "bin" / ("rg.exe" if windows else "rg")).read_bytes() == b"a stand-in rg"
    assert not (folder / ".rg").exists() and not (p.home / "downloads").exists()
    assert sorted(web.asked) == sorted(web.files)
    kept = p.home / "config" / "npm" / "earendil-works+pi-coding-agent@1.5.2"
    assert json.loads((kept / "package-lock.json").read_text(encoding="utf-8"))["packages"][
        "node_modules/@earendil-works/pi-coding-agent"]["integrity"] == constants.INTEGRITY
    said = " ".join(answer["lines"])
    assert "its sha512, as npm's lock file records it, is the one pinned in this plugin" in said
    assert refused(lambda: p.install(True)) == "Pi 1.5.2 is installed already"


def test_a_reinstall_of_the_same_pin_installs_the_kept_lock_again(windows, monkeypatch, node_pins):
    p = windows
    npm = Npm()
    p.out = type(p.out)(**{**p.out.__dict__, "streamer": npm})
    p.out.opener = served(monkeypatch, p, node_pins)
    assert p.install(True, log=Output())["ok"] is True
    assert p.uninstall(True)["ok"] is True and p.installed() is None
    p.out.opener = served(monkeypatch, p, node_pins)
    answer = p.install(True, log=Output())
    assert answer["ok"] is True and [r["argv"][2] for r in npm.ran] == ["install", "ci"]
    assert npm.ran[1]["argv"][3:] == ["--prefix", str(p.home / "app" / "1.5.2" / "cli"), "--ignore-scripts",
                                      "--no-audit", "--no-fund", "--no-update-notifier"]
    assert any("installed again from the lock kept in" in line for line in answer["lines"])


def test_another_sha512_puts_nothing_in_use_and_leaves_the_one_in_use(tmp_path, monkeypatch, node_pins):
    other = "sha512-" + "A" * 86 + "=="
    p = made(tmp_path, streamer=Npm(integrity=other))
    installed(p, "1.5.1")
    p.out.opener = served(monkeypatch, p, node_pins)
    answer = p.install(True, log=Output())
    assert answer["ok"] is False and "with another sha512 than the one pinned in this plugin" in answer["said"]
    assert p.current().name == "1.5.1" and not (p.home / "app" / "1.5.2").exists()
    assert not (p.home / "config" / "npm" / "earendil-works+pi-coding-agent@1.5.2" / "package-lock.json").exists()


def test_a_failed_npm_and_an_archive_without_its_program_install_nothing(tmp_path, monkeypatch, node_pins):
    p = made(tmp_path / "npm", streamer=Npm(code=1))
    p.out.opener = served(monkeypatch, p, node_pins)
    answer = p.install(True, log=Output())
    assert answer["ok"] is False and "npm ended with exit code 1" in answer["said"]
    assert "npm error code E404" in answer["said"] and p.installed() is None
    assert not (p.home / "app" / "1.5.2").exists()

    q = made(tmp_path / "rg", streamer=Npm())
    web = served(monkeypatch, q, node_pins)
    from conftest import zipped
    import hashlib
    empty = zipped({"ripgrep-15.1.0-x86_64-pc-windows-msvc/COPYING": b"no program"})
    name = constants.RIPGREP_BUILDS[("windows", "x64")][0]
    monkeypatch.setitem(constants.RIPGREP_BUILDS, ("windows", "x64"),
                        (name, len(empty), hashlib.sha256(empty).hexdigest()))
    web.files[constants.RIPGREP_FILES + name] = empty
    q.out.opener = web
    answer = q.install(True, log=Output())
    assert answer["ok"] is False and f"{name} holds no rg.exe: Pi is not installed" in answer["said"]
    assert q.installed() is None and not (q.home / "app" / "1.5.2").exists()


def test_install_asks_its_licence_first_and_refuses_in_words_before_anything(windows, monkeypatch, node_pins):
    p = windows
    p.out.opener = web = served(monkeypatch, p, node_pins)
    e = pytest.raises(ValueError, p.install).value
    assert e.accept == "accept_licence" and web.asked == [] and not (p.home / "app").exists()
    form = next(f for f in p.status()["forms"] if f["id"] == "ai-install")
    assert form["job"] is True and form["fields"][0]["name"] == "accept_licence"
    assert form["confirm"]["words"].startswith("Node.js 24.22.3 (node-v24.22.3-win-x64.zip), Pi 1.5.2 with the "
                                               "packages npm resolves for it")
    assert form["fields"][0]["words"].startswith("Pi: MIT (its authors, earendil-works/pi).")


def test_uninstall_leaves_what_it_keeps(windows):
    p = windows
    installed(p)
    session = p.sessions_dir() / "--project--" / "one.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text("{}", encoding="utf-8")
    answer = p.uninstall(True)
    assert answer["ok"] is True and p.installed() is None and not (p.home / "app").exists()
    assert session.exists()
    assert p.package().keeps.startswith(f"What it kept stays: {p.config_dir()}, with its sessions")


def test_a_pi_of_yours_is_a_fact_never_run(tmp_path):
    p = made(tmp_path, "windows")
    yours = tmp_path / "npm" / "pi.cmd"
    yours.parent.mkdir()
    yours.write_bytes(b"yours")
    p.out.which = lambda name, *a, **k: str(yours) if name == "pi" else None
    assert p.yours() == str(yours)
    assert p.status()["yours"] == f"{yours} is yours: left as it is, not used from here"
    installed(p)
    chosen(p)
    launch = p._launch(str(tmp_path), p.use_kept(), p.serving_of("ollama/default"), "")
    assert str(yours) not in launch.argv and launch.argv[0].endswith("node.exe")
    mine = Path(p.installed().path)
    p.out.which = lambda name, *a, **k: str(mine)
    assert p.yours() == ""  # (its own is not yours)


def test_no_command_it_names_runs_npm_a_package_install_or_a_sign_in(tmp_path):
    p = made(tmp_path, "windows")
    installed(p)
    chosen(p)
    launch = p._launch(str(tmp_path), p.use_kept(), p.serving_of("ollama/default"), "")
    text = " ".join(launch.argv)
    for word in ("npm", "install", "/login", "/share", "--offline=false", "pi.cmd", "--no-extensions", "update"):
        assert word not in text, word
