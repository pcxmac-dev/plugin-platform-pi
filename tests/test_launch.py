"""How Pi is started (the plan's X2 and the pre-build checks, C-P1): each model server's start as Pi reads its files
(Ollama found here; llama.cpp with a key; vLLM on another machine over plain http; LMDeploy), golden models.json,
mcp.json and settings.json written into its own agent folder; the exact command, folder and environment of a window
on Windows and the lines to paste on both systems; the key and the token in no command, no file and no line; Git for
Windows' bash found in each of its folders and missing, WSL's launcher never chosen; a planted folder refused; values
Pi would read as more than text refused; its tools placed; Liminal's MCP through the bridge; its older sessions pruned
as a window opens, and never by Command… or while a window is open.

Nothing is started: the window's process is a stand-in, the platform and the login are stand-ins."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from conftest import (BRIDGE, CODER, DATA, DECLARED, HTTP, KEY, KEY_VARIABLE, agent_file, chosen, git_bash, installed,
                      made, refused)
from liminal_libs import console
from liminal_libs.machines import children
from liminal_libs.machines.children import PLACEHOLDER
from liminal_libs.machines.harness import BREAKAWAY, NEW_CONSOLE, RUN_IT
from plugin_platform_pi import constants, files, page

SERVED = {  # each recorded row: its model, its golden models.json
    "ollama/default": ("qwen3:8b", "models-ollama.json"),
    "llamacpp/gpu": (CODER, "models-llamacpp.json"),
    "vllm/box": ("Qwen/Qwen3-8B", "models-vllm.json"),
}


def golden(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def node_of(p) -> str:
    folder = p.home / "app" / constants.PIN / "node"
    return str(folder / "node.exe") if p.system == "windows" else str(folder / "bin" / "node")


def cli_of(p) -> str:
    return str(p.home / "app" / constants.PIN / "cli" / "node_modules" / "@earendil-works" / "pi-coding-agent" /
               "dist" / "bundle" / "cli.js")


def started(p, folder, key: str = ""):
    """The launch of a start in `folder` against what Use… keeps."""
    use = p.use_kept()
    return p._launch(str(folder), use, p.serving_of(use.server), key)


def bash_of(tmp_path) -> str:
    return str(tmp_path.joinpath("win", "ProgramFiles", "Git", "bin", "bash.exe"))


# -- each model server ------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("system", ["windows", "linux"])
@pytest.mark.parametrize("server", list(SERVED))
def test_each_start_writes_its_golden_files_and_is_told_its_model(tmp_path, project, system, server):
    p = made(tmp_path, system)
    installed(p)
    model, models = SERVED[server]
    chosen(p, server, model)
    launch = started(p, project, PLACEHOLDER if server == "llamacpp/gpu" else "")
    assert list(launch.argv) == [node_of(p), cli_of(p), "-e", str(p.extension_path()), "--provider", "liminal",
                                 "--model", model]
    assert launch.cwd == str(project)
    assert agent_file(p, "models.json") == golden(models)
    assert agent_file(p, "mcp.json") == golden("mcp-off.json")
    settings = agent_file(p, "settings.json")
    if system == "windows":
        assert settings == {**golden("settings-linux.json"), "shellPath": bash_of(tmp_path)}
    else:
        assert settings == golden("settings-linux.json")
    assert settings["defaultProjectTrust"] == "never"
    assert p.extension_path().read_text(encoding="utf-8") == (DATA / "permission.ts").read_text(encoding="utf-8")
    assert p.extension_path().parent.name == "liminal" and "extensions" not in p.extension_path().parts


def test_lmdeploy_is_started_as_any_openai_compatible_server(windows, project):
    """All four engines qualify (the base's fit: an OpenAI-compatible address); Pi asks chat completions alone."""
    p = windows
    installed(p)
    chosen(p, "lmdeploy/turbo", "internlm3-8b")
    assert p.fits(p.serving_of("lmdeploy/turbo")) == ""
    started(p, project)
    assert agent_file(p, "models.json")["providers"]["liminal"]["baseUrl"] == HTTP + "127.0.0.1:23333/v1"


def test_a_window_on_windows_is_started_with_its_command_its_folder_and_its_environment(windows, project, tmp_path):
    p = windows
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    answer = p.open(str(project))
    [start] = p.out.popen.made
    words = started(p, project, KEY).argv
    assert start["argv"] == console.hold_command(list(words))
    assert start["cwd"] == str(project) and start["creationflags"] == NEW_CONSOLE | BREAKAWAY
    env = start["env"]
    assert {n: env[n] for n in ("PI_CODING_AGENT_DIR", "PI_CODING_AGENT_SESSION_DIR", "PI_OFFLINE", "PI_TELEMETRY",
                                "PI_SKIP_VERSION_CHECK", "NoDefaultCurrentDirectoryInExePath", "LIMINAL_SERVER_KEY",
                                "PATH", "NODE_COMPILE_CACHE")} == {
        "PI_CODING_AGENT_DIR": str(p.agent_dir()), "PI_CODING_AGENT_SESSION_DIR": str(p.sessions_dir()),
        "PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PI_SKIP_VERSION_CHECK": "1",
        "NoDefaultCurrentDirectoryInExePath": "1", "LIMINAL_SERVER_KEY": KEY,
        "PATH": "C:\\Windows\\System32;C:\\tools", "NODE_COMPILE_CACHE": str(p.config_dir() / "pi" / "compile-cache")}
    for name in ("ANTHROPIC_API_KEY", "MASSIVE_API_KEY", "PI_OAUTH_CALLBACK_HOST", "NODE_OPTIONS",
                 "npm_config_registry", KEY_VARIABLE, "LIMINAL_PLATFORM_DIR"):
        assert name not in env, name
    assert answer["ok"] is True and answer["said"] == (f"Pi opened in a window of its own in {project}, started "
                                                       f"against llama.cpp / gpu with {CODER}")
    assert not any(KEY in word for word in start["argv"]) and KEY not in str(answer)
    for name in ("models.json", "mcp.json", "settings.json"):
        assert KEY not in (p.agent_dir() / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_the_lines_to_paste_hold_no_key_and_end_in_its_command(tmp_path, project, system):
    p = made(tmp_path, system, interactive=False)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    answer = p.command(str(project))
    lines = answer["lines"]
    assert answer["ok"] is True and answer["said"] == RUN_IT
    assert p.open(str(project)) == answer  # no window here: the same lines
    assert p.out.popen.made == [] and not any(KEY in line for line in lines)
    assert sum(PLACEHOLDER in line for line in lines) == 1
    assert any("LIMINAL_SERVER_KEY" in line and PLACEHOLDER in line for line in lines)
    for name in ("ANTHROPIC_API_KEY", "PI_CODING_AGENT_DIR", "NODE_OPTIONS", KEY_VARIABLE, "MASSIVE_API_KEY"):
        unset = f"Remove-Item Env:{name} -ErrorAction SilentlyContinue" if system == "windows" else f"unset {name}"
        assert unset in lines, name
    last = lines[-1]
    assert cli_of(p) in last and str(p.extension_path()) in last and "--provider" in last and "liminal" in last
    assert any("PI_OFFLINE" in line for line in lines)
    assert any("NoDefaultCurrentDirectoryInExePath" in line for line in lines) is (system == "windows")


def test_what_pi_inherits_drops_every_hosted_key_every_pi_node_and_npm_setting_and_every_pair_of_liminals(
        windows, project):
    p = windows
    installed(p)
    chosen(p)
    launch = started(p, project)
    assert launch.drop == (*constants.DROP, *DECLARED, "LIMINAL_*") and launch.secret == ()
    for pattern in ("PI_*", "NODE_*", "npm_config_*", "ANTHROPIC_*", "OPENAI_*", "OLLAMA_*", "OTEL_*", "CODEX_*"):
        assert pattern in constants.DROP, pattern
    keyed = started(p, project, KEY)
    assert keyed.secret == ("LIMINAL_SERVER_KEY",) and keyed.env["LIMINAL_SERVER_KEY"] == KEY
    assert not any(KEY in word for word in keyed.argv)
    assert "NoDefaultCurrentDirectoryInExePath" in launch.env


def test_on_linux_no_windows_switch_or_shell_is_written(linux, project):
    installed(linux)
    chosen(linux)
    launch = started(linux, project)
    assert "NoDefaultCurrentDirectoryInExePath" not in launch.env
    assert launch.env["PATH"] == "/usr/local/bin:/usr/bin"  # (the empty entry, the folder Pi is in, left out)
    assert "shellPath" not in agent_file(linux, "settings.json")


def test_the_context_not_said_or_too_small_is_refused_and_a_typed_one_is_used(windows, project):
    p = windows
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)  # its model lists no context: the instance's own (65536) is used
    started(p, project)
    assert agent_file(p, "models.json")["providers"]["liminal"]["models"][0]["contextWindow"] == 65536
    p.app.serving["llamacpp"]["instances"][0]["context"] = None
    p._forget_servers()
    assert refused(lambda: p.command(str(project))) == ("llama.cpp / gpu does not say "
                                                        f"{CODER}'s context: give it under Use… (Context)")
    p.app.serving["llamacpp"]["instances"][0]["context"] = 4096  # the server's word, under what Pi is given
    p._forget_servers()
    assert "8,192 tokens at the least" in refused(lambda: p.command(str(project)))
    chosen(p, "llamacpp/gpu", CODER, context=32768)
    started(p, project)
    assert agent_file(p, "models.json")["providers"]["liminal"]["models"][0] == {
        "id": CODER, "name": CODER, "input": ["text"], "contextWindow": 32768, "maxTokens": 8192}


def test_tools_follow_the_servers_word_and_the_choice(windows, project):
    p = windows
    installed(p)
    chosen(p, "ollama/default", "gemma3:4b")  # its server says it calls no tools
    assert started(p, project).argv[-1] == "--no-tools"
    chosen(p, "ollama/default", "gemma3:4b", tools="yes")
    assert "--no-tools" not in started(p, project).argv
    chosen(p, "ollama/default", "qwen3:8b", tools="no")
    assert started(p, project).argv[-1] == "--no-tools"
    chosen(p, "llamacpp/gpu", CODER)  # says nothing: yes
    assert "--no-tools" not in started(p, project).argv


@pytest.mark.parametrize("model", ["${HOME}", "a$(id)b", "!whoami", "$HOME", "q$x"])
def test_a_model_id_pi_would_read_as_more_than_text_is_refused(windows, project, model):
    p = windows
    installed(p)
    chosen(p, "ollama/default", model)
    words = refused(lambda: p.command(str(project)))
    assert "cannot be written into a harness's configuration as it is" in words or "model" in words
    assert not (p.agent_dir() / "models.json").exists()


def test_an_address_pi_would_read_as_more_than_text_is_refused_and_nothing_written(windows, project):
    p = windows
    installed(p)
    p.app.serving["ollama"]["instances"][0]["openai"] = HTTP + "127.0.0.1:11434/v1?k=$SECRET"
    chosen(p)
    assert "the server's address cannot be written" in refused(lambda: p.command(str(project)))
    assert not (p.agent_dir() / "models.json").exists()


# -- its shell on Windows ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("under", ["ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"])
def test_git_bash_is_found_in_each_of_its_folders(tmp_path, project, under):
    p = made(tmp_path, "windows", bash=False)
    found = git_bash(tmp_path, under)
    installed(p)
    chosen(p)
    assert p.git_bash() == str(found)
    started(p, project)
    assert agent_file(p, "settings.json")["shellPath"] == str(found)


def test_without_git_bash_pi_is_refused_naming_where_it_looked(tmp_path, project):
    p = made(tmp_path, "windows", bash=False)
    installed(p)
    chosen(p)
    words = refused(lambda: p.command(str(project)))
    for path in p.bash_looked():
        assert path in words
    assert len(p.bash_looked()) == 3
    assert "Installing Git for Windows is yours to do" in words and "WSL's launcher" in words
    assert not (p.agent_dir() / "settings.json").exists()
    status = p.status()
    assert "no Git for Windows' bash is installed" in status["problem"]


def test_wsls_bash_is_never_chosen_even_first_on_path(tmp_path, project):
    p = made(tmp_path, "windows", bash=False)
    wsl = tmp_path / "win" / "Windows" / "System32" / "bash.exe"
    wsl.parent.mkdir(parents=True)
    wsl.write_bytes(b"MZ wsl")
    p.out = type(p.out)(**{**p.out.__dict__, "which": lambda name, *a, **k: str(wsl)})
    installed(p)
    chosen(p)
    assert p.git_bash() == ""
    assert "Installing Git for Windows is yours to do" in refused(lambda: p.command(str(project)))
    # nor where a folder Git for Windows is looked for in is WSL's own
    p.out.env["LOCALAPPDATA"] = str(tmp_path / "win" / "LocalAppData")
    alias = tmp_path / "win" / "LocalAppData" / "Programs" / "Git" / "bin" / "bash.exe"
    alias.parent.mkdir(parents=True)
    alias.write_bytes(b"MZ git")
    assert p.git_bash() == str(alias)
    from plugin_platform_pi import _wsl_launcher
    assert _wsl_launcher("C:\\Windows\\System32\\bash.exe") and _wsl_launcher("C:/Windows/Sysnative/BASH.EXE")
    assert _wsl_launcher("C:\\Users\\you\\AppData\\Local\\Microsoft\\WindowsApps\\bash.exe")
    assert not _wsl_launcher(str(alias)) and not _wsl_launcher("C:\\Program Files\\Git\\bin\\bash.exe")


# -- a planted folder --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["git.exe", "rg.EXE", "bash.cmd", "where.com", "fd.bat", "node.exe", "taskkill.exe",
                                  "npm.cmd", "pwsh.ps1"])
def test_a_folder_holding_a_program_pi_would_run_from_there_is_refused_on_windows(windows, project, name):
    p = windows
    installed(p)
    chosen(p)
    (project / name).write_bytes(b"planted")
    words = refused(lambda: p.command(str(project)))
    assert words == page.planted(str(project), name)
    assert not (p.agent_dir() / "models.json").exists()


def test_a_folder_holding_other_files_opens_and_linux_looks_at_no_folder(windows, linux, project):
    (project / "git.txt").write_text("notes", encoding="utf-8")
    (project / "readme.md").write_text("hi", encoding="utf-8")
    for p in (windows, linux):
        installed(p)
        chosen(p)
        assert p.command(str(project))["ok"] is True
    (project / "git").write_bytes(b"#!/bin/sh")
    assert linux.planted(str(project)) == ""


# -- its tools ---------------------------------------------------------------------------------------------------------
def test_its_tools_are_placed_where_pi_looks_and_replaced_when_another_is_there(windows, project):
    p = windows
    folder = installed(p)
    chosen(p)
    started(p, project)
    placed = p.agent_dir() / "bin" / "rg.exe"
    assert placed.read_bytes() == (folder / "bin" / "rg.exe").read_bytes()
    placed.write_bytes(b"another rg")
    assert p.place_tools(folder) == ["rg.exe"] and placed.read_bytes() == b"a stand-in rg"
    assert p.place_tools(folder) == []  # the same: not copied again
    assert not (p.agent_dir() / "bin" / "fd.exe").exists()  # fd is not pinned in this release


def test_pis_own_note_of_its_changelog_is_kept_and_the_rest_of_its_settings_replaced(windows, project):
    p = windows
    installed(p)
    chosen(p)
    (p.agent_dir()).mkdir(parents=True)
    (p.agent_dir() / "settings.json").write_text(json.dumps({"lastChangelogVersion": "1.5.2",
                                                            "packages": ["npm:x"], "defaultProjectTrust": "always"}),
                                                 encoding="utf-8")
    started(p, project)
    assert agent_file(p, "settings.json") == {"lastChangelogVersion": "1.5.2", "defaultProjectTrust": "never",
                                              "enableInstallTelemetry": False, "shellPath": p.git_bash()}


def test_not_installed_or_unpinned_is_refused(windows, project, monkeypatch):
    p = windows
    chosen(p)
    assert refused(lambda: p.command(str(project))) == "Pi is not installed here: Install… first"
    installed(p)
    monkeypatch.setattr(constants, "NODE_BUILDS", {})
    assert refused(lambda: p.command(str(project))) == page.unpinned("Windows on x64")


# -- Liminal's MCP -----------------------------------------------------------------------------------------------------
def test_liminals_mcp_through_the_bridge_with_a_token_for_the_window_alone(tmp_path, project):
    p = made(tmp_path, "windows", mcp=True)
    installed(p)
    chosen(p, mcp="on")
    answer = p.open(str(project))
    [start] = p.out.popen.made
    [token] = p.app.minted
    assert answer["ok"] is True and start["env"]["LIMINAL_MCP_TOKEN"] == token
    assert not any(token in w for w in start["argv"])
    for name in ("models.json", "mcp.json", "settings.json"):
        assert token not in (p.agent_dir() / name).read_text(encoding="utf-8")
    assert agent_file(p, "mcp.json") == golden("mcp-bridge.json")  # the hold (50 s) and a minute more
    # its tools pass the permission step unasked: the MCP plugin grants and holds them
    assert p.extension_path().read_text(encoding="utf-8") == (DATA / "permission-mcp.ts").read_text(encoding="utf-8")
    lines = p.command(str(project))["lines"]
    assert not any(token in line for line in lines) and len(p.app.minted) == 1  # Command… asks no token
    p.out.popen.windows[0].code = 0
    p.running()
    assert p.app.ended == [token]  # the window gone: its token ended


def test_an_mcp_plugin_offering_only_http_is_refused_in_words(tmp_path, project):
    p = made(tmp_path, "windows", mcp=True, interactive=False)
    p.app.offer = {**p.app.offer, "wires": ["http"]}
    installed(p)
    chosen(p, mcp="on")
    words = refused(lambda: p.command(str(project)))
    assert "the MCP plugin serves the MCP plugin's address on the platform (HTTP) here" in words
    assert "reaches it by the MCP plugin's bridge (stdio) alone" in words


@pytest.mark.parametrize("system, bridge", [("windows", ["python.exe", *BRIDGE[1:]]),
                                            ("linux", ["python3", "-I", "/x/bridge.py"]),
                                            ("linux", BRIDGE)])  # (a Windows path is no whole path on Linux)
def test_a_bridge_not_named_by_a_whole_path_is_refused(tmp_path, project, system, bridge):
    p = made(tmp_path, system, mcp=True, interactive=False)
    p.app.offer = {**p.app.offer, "bridge": bridge}
    installed(p)
    chosen(p, mcp="on")
    assert refused(lambda: p.command(str(project))) == ("Pi cannot be given what this start needs: the MCP plugin's "
                                                        "bridge is not named by a whole path. Nothing was started")


def test_liminals_mcp_off_writes_no_server(windows, project):
    installed(windows)
    chosen(windows)
    started(windows, project)
    assert agent_file(windows, "mcp.json") == {"mcpServers": {}}
    assert windows.app.asked and not any(name == "mcp" for name, _, _ in windows.app.asked)


# -- its sessions ------------------------------------------------------------------------------------------------------
def sessions(p, count: int, size: int = 10) -> list[Path]:
    """`count` stand-in sessions, the oldest first, laid out under its sessions folder by the folder they were in."""
    made_ = []
    for n in range(count):
        path = p.sessions_dir() / f"--project-{n % 3}--" / f"2026-11-{n % 28 + 1:02d}_{n:04d}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
        os.utime(path, (1_000_000 + n, 1_000_000 + n))
        made_.append(path)
    return made_


def test_an_open_that_opens_a_window_keeps_the_newest_hundred_sessions(windows, project):
    p = windows
    installed(p)
    chosen(p)
    kept = sessions(p, 110)
    other = p.sessions_dir() / "notes.txt"
    other.write_text("not a session", encoding="utf-8")
    answer = p.open(str(project))
    assert answer["ok"] is True and answer["lines"][-1] == "10 older sessions removed"
    assert [x.exists() for x in kept] == [False] * 10 + [True] * 100 and other.exists()


def test_sessions_past_their_bytes_go_too_and_their_empty_folders(windows, monkeypatch):
    p = windows
    monkeypatch.setattr(constants, "SESSIONS_BYTES", 250)
    made_ = sessions(p, 4, size=100)
    assert p.prune_sessions() == 2 and [x.exists() for x in made_] == [False, False, True, True]


def test_no_session_is_removed_by_command_or_while_a_window_is_open(windows, project):
    p = windows
    installed(p)
    chosen(p)
    kept = sessions(p, 105)
    p.command(str(project))
    assert all(x.exists() for x in kept)  # Command… is a read
    assert p.open(str(project))["ok"] is True and sum(x.exists() for x in kept) == 100
    for n in range(5):  # five newer while the window is open
        path = p.sessions_dir() / "late" / f"late{n}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"y")
        os.utime(path, (3_000_000 + n, 3_000_000 + n))
    answer = p.open(str(project))
    assert answer["ok"] is True and "older sessions removed" not in " ".join(answer["lines"])
    assert sum(x.exists() for x in kept) == 100


def test_the_launch_is_told_whole_paths(tmp_path, project, monkeypatch):
    p = made(tmp_path, "windows")
    installed(p)
    chosen(p)
    monkeypatch.chdir(tmp_path)
    launch = started(p, project)
    for word in (launch.argv[0], launch.argv[1], launch.argv[3], launch.env["PI_CODING_AGENT_DIR"],
                 launch.env["PI_CODING_AGENT_SESSION_DIR"]):
        assert Path(word).is_absolute(), word
    assert all(not children.not_passed(w) for w in launch.argv)
    assert files.arguments(extension=str(p.extension_path()), model="qwen3:8b", tools=True) == list(launch.argv[2:])
