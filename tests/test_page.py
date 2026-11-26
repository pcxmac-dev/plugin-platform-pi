"""Its Main: a status that runs nothing, writes nothing and asks nothing over the network; Before you use it for each
model server and each system (what it asks before it acts, the user's answer 7; its ports, answer 8; its .pi/ and
AGENTS.md; its shell; its Node.js; its tools; its sessions); Open…'s confirmation ending in what Pi must say; its facts
and its problems; its API facts asking nothing."""
from __future__ import annotations

import pytest

from conftest import CODER, chosen, form, installed, made, never, rows
from plugin_platform_pi import page


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_main_runs_nothing_writes_nothing_and_asks_nothing_over_the_network(tmp_path, system):
    p = made(tmp_path, system)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER)
    p.out.popen = never("a window")  # the opener, the streamer, the runner, a port and an instance refuse already
    status = p.status()
    assert status["valid"] is True and status["summary"] == "Pi 1.5.2" and "problem" not in status
    assert [t["title"] for t in status["tables"]] == ["Before you use it", "Model servers"]
    assert status["uses"] == f"llama.cpp / gpu: {CODER}"
    assert {a for _, a, _ in p.app.asked} == {"serving"}  # its model servers, through the app
    assert not p.config_dir().exists()  # a status writes nothing
    assert status["pinned"].startswith("Pi 1.5.2 on Node.js 24.22.3 (node-v24.22.3-")


def test_before_you_use_it_for_ollama_on_windows(windows, tmp_path):
    p = windows
    installed(p)
    chosen(p)
    said = rows(p.status())
    assert list(said) == ["It asks before it acts", "Local only", "/share and /bug", "The folder's .pi and AGENTS.md",
                          "Its shell", "Its Node.js", "Its tools", "Its ports", "Its sessions", "The model",
                          "What it shares with a Pi of yours", "Its configuration"]
    asks = said["It asks before it acts"]
    assert asks.startswith("Pi itself asks nothing before a tool call and has no sandbox: in its makers' words it does "
                           "not ask for approval before every tool call.")
    assert "asks you on Pi's screen before each shell command, each edit, each write and every other tool" in asks
    assert "Its reads (read, grep, find, ls) are not asked, and read whatever you can read." in asks
    assert "runs at once with your rights, with no sandbox, including commands that reach this machine's platform" \
        in asks
    local = said["Local only"]
    assert local.startswith("The one model server it is given is Ollama / default")
    for words in ("PI_OFFLINE=1", "PI_TELEMETRY=0", "PI_SKIP_VERSION_CHECK=1", "enableInstallTelemetry",
                  "no download of fd or ripgrep", "User-Agent"):
        assert words in local, words
    assert said["/share and /bug"] == page.SHARE and "Nothing does so by itself." in page.SHARE
    folder = said["The folder's .pi and AGENTS.md"]
    assert "is not loaded" in folder and "AGENTS.md or CLAUDE.md" in folder and "loaded all the same" in folder
    assert "--no-context-files" in folder and "not passed from here" in folder
    shell = said["Its shell"]
    assert str(tmp_path / "win" / "ProgramFiles" / "Git" / "bin" / "bash.exe") in shell
    assert "never used from here" in shell and "Windows Terminal" in shell and "NoDefaultCurrentDirectoryInExePath" \
        in shell
    assert said["Its Node.js"].startswith("It runs on a Node.js 24.22.3 of its own")
    assert "pinned in no file of this plugin's" in said["Its Node.js"]
    assert "ripgrep 15.1.0" in said["Its tools"] and "fd is not pinned in this release" in said["Its tools"]
    assert said["Its ports"] == page.PORTS and "opens no port by itself" in page.PORTS
    assert str(p.sessions_dir()) in said["Its sessions"] and "newest 100 (200 MB at the most)" in said["Its sessions"]
    assert said["The model"] == (page.MODEL + " It is told 40,960 tokens of context (as Ollama / default says it).")
    assert str(p.agent_dir()) in said["What it shares with a Pi of yours"]
    assert str(p.extension_path()) in said["Its configuration"]


def test_its_rows_for_a_key_plain_http_and_liminals_mcp(tmp_path):
    p = made(tmp_path, "linux", mcp=True)
    installed(p)
    chosen(p, "llamacpp/gpu", CODER, mcp="on")
    said = rows(p.status())
    assert said["Its key"] == page.KEYED.format(server="llama.cpp / gpu")
    assert said["Its shell"] == page.LINUX
    assert "LIMINAL_MCP_TOKEN" in said["Liminal's MCP"] and "could still read Pi's own environment" in \
        said["Liminal's MCP"]
    chosen(p, "vllm/box", "Qwen/Qwen3-8B")
    said = rows(p.status())
    assert said["Plain http"] == page.PLAIN.format(server="vLLM / box") and "Liminal's MCP" not in said


def test_tools_said_with_the_model(windows):
    p = windows
    installed(p)
    chosen(p, "ollama/default", "gemma3:4b")
    assert "It is started with no tools" in rows(p.status())["The model"]
    chosen(p, "ollama/default", "gemma3:4b", tools="yes")
    assert "Its server says the model calls no tools, and Use… says it does" in rows(p.status())["The model"]


def test_before_a_choice_its_rows_say_what_holds_for_any_server(windows):
    installed(windows)
    said = rows(windows.status())
    assert said["Local only"].startswith("The one model server it is given is the model server you choose (Use…)")
    assert said["The model"] == page.MODEL


def test_without_git_bash_its_shell_row_and_its_problem_say_so(tmp_path):
    p = made(tmp_path, "windows", bash=False)
    installed(p)
    status = p.status()
    shell = rows(status)["Its shell"]
    assert shell.startswith("On Windows Pi needs Git for Windows' bash, and none is installed where Git for Windows "
                            "puts it:")
    assert "Installing Git for Windows is yours to do" in shell
    assert status["problem"].startswith("no Git for Windows' bash is installed (")
    assert "shell" not in status


def test_its_facts_a_pi_of_yours_and_its_shell(windows, tmp_path):
    p = windows
    status = p.status()
    assert status["shell"] == "Git for Windows' bash: " + str(tmp_path / "win" / "ProgramFiles" / "Git" / "bin" /
                                                              "bash.exe")


def test_open_ends_in_what_pi_must_say(windows):
    p = windows
    installed(p)
    chosen(p)
    confirm = form(p.status(), "ai-open")["confirm"]["words"]
    assert confirm.endswith(page.open_words(window=True))
    assert "Pi acts as you with no sandbox: this plugin's permission step asks you on its screen before each " \
           "command, edit and write (its reads are not asked)" in confirm
    assert "its AGENTS.md and CLAUDE.md are" in confirm and "the newest 100 are kept" in confirm
    assert page.open_words(window=False).endswith("older sessions are removed at the next Open… that opens a window.")


def test_its_api_facts_ask_nothing(windows):
    p = windows
    installed(p)
    chosen(p)
    facts = p.api_facts()
    assert facts["Pi coding agent"]["Installed"].startswith("1.5.2 in ")
    assert facts["Pi coding agent"]["Started against"] == "ollama/default: qwen3:8b"
    assert facts["npm registry"]["Pinned"].startswith("@earendil-works/pi-coding-agent@1.5.2 (sha512-mUWI04rqF1Vd")
    assert facts["Node.js"]["This system's archive"] == "node-v24.22.3-win-x64.zip"
    assert {a for _, a, _ in p.app.asked} <= {"serving"}
