"""What Pi is given, as files.py makes it: models.json, mcp.json and settings.json against the goldens in tests/data
(written once from the functions and read line by line), the permission step's text, and the words of its command
line. Each as C-P1 read Pi 1.5.2 at the tag: the apiKey a variable's name or a literal, never a value Pi would run;
Liminal's MCP as a stdio server naming the token's variable; every folder untrusted; the shell by its whole path on
Windows; the tool_call event held for your answer, and refused where none can be had."""
from __future__ import annotations

import json
import re

import pytest

from conftest import BRIDGE, CODER, DATA, HTTP, KEY
from plugin_platform_pi import constants, files


def golden(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def values(data) -> list[str]:
    """Every text in a JSON value, its keys among them."""
    if isinstance(data, dict):
        return [*(str(k) for k in data), *(v for item in data.values() for v in values(item))]
    if isinstance(data, list):
        return [v for item in data for v in values(item)]
    return [data] if isinstance(data, str) else []


@pytest.mark.parametrize(("name", "address", "model", "context", "keyed"), [
    ("models-ollama.json", HTTP + "127.0.0.1:11434/v1", "qwen3:8b", 40960, False),
    ("models-llamacpp.json", HTTP + "127.0.0.1:9931/v1", CODER, 65536, True),
    ("models-vllm.json", HTTP + "gpu-box.example.test:8000/v1", "Qwen/Qwen3-8B", 32768, False),
])
def test_models_json_is_its_golden_for_each_recorded_row(name, address, model, context, keyed):
    made = files.models_json(base_url=address, model=model, context=context, keyed=keyed)
    assert made == golden(name)
    assert files.text(made) == (DATA / name).read_text(encoding="utf-8")
    provider = made["providers"]["liminal"]
    assert list(made["providers"]) == ["liminal"] and provider["api"] == "openai-completions"
    assert provider["apiKey"] == ("${LIMINAL_SERVER_KEY}" if keyed else "none")
    assert not any(v.lstrip().startswith("!") for v in values(made))  # a value Pi would run as a command: none
    assert KEY not in files.text(made)


def test_a_models_output_is_a_quarter_of_its_context_and_8192_at_the_most():
    assert [files.output(c) for c in (8192, 16384, 32768, 65536, 2_000_000)] == [2048, 4096, 8192, 8192, 8192]


def test_mcp_json_is_no_server_while_liminals_mcp_is_off_and_the_bridge_while_it_is_on():
    assert files.mcp_json() == golden("mcp-off.json") == {"mcpServers": {}}
    on = files.mcp_json(BRIDGE, 110)
    assert on == golden("mcp-bridge.json")
    entry = on["mcpServers"]["liminal"]
    assert [entry["command"], *entry["args"]] == BRIDGE and entry["timeout"] == 50 + 60
    assert entry["env"] == {"LIMINAL_MCP_TOKEN": "${LIMINAL_MCP_TOKEN}"}  # Pi resolves it from its environment
    assert "headers" not in entry and "url" not in entry  # stdio alone


def test_settings_json_untrusts_every_folder_and_names_the_shell_on_windows():
    windows = files.settings_json(system="windows", shell_path="C:\\Program Files\\Git\\bin\\bash.exe")
    assert windows == golden("settings-windows.json")
    assert files.settings_json(system="linux") == golden("settings-linux.json")
    assert windows["defaultProjectTrust"] == "never" and windows["enableInstallTelemetry"] is False
    with pytest.raises(ValueError, match="whole path"):
        files.settings_json(system="windows", shell_path="")


def test_settings_json_keeps_pis_own_note_of_its_changelog_and_nothing_else_of_the_file():
    kept = {"lastChangelogVersion": "1.5.2", "packages": ["npm:evil"], "extensions": ["/tmp/x.ts"],
            "defaultProjectTrust": "always", "shellPath": "C:\\Windows\\System32\\bash.exe", "npmCommand": "evil"}
    made = files.settings_json(system="windows", shell_path="C:\\Git\\bin\\bash.exe", kept=kept)
    assert made == {"lastChangelogVersion": "1.5.2", "defaultProjectTrust": "never", "enableInstallTelemetry": False,
                    "shellPath": "C:\\Git\\bin\\bash.exe"}
    for odd in ("!rm -rf /", "1.5.2; x", 7, "", "9" * 41):
        assert "lastChangelogVersion" not in files.settings_json(system="linux", kept={"lastChangelogVersion": odd})


def test_its_command_line_names_the_permission_step_the_provider_and_the_model():
    words = files.arguments(extension="C:\\pi\\config\\pi\\liminal\\permission.ts", model="qwen3:8b", tools=True)
    assert words == ["-e", "C:\\pi\\config\\pi\\liminal\\permission.ts", "--provider", "liminal", "--model",
                     "qwen3:8b"]
    assert files.arguments(extension="/x.ts", model="m", tools=False)[-1] == "--no-tools"
    assert "--no-extensions" not in words  # it would turn off Pi's own MCP extension too (C-P1.1)
    assert "--no-context-files" not in words  # the plan's choice: left on, said on the page


# -- the permission step -----------------------------------------------------------------------------------------------
@pytest.fixture
def step() -> str:
    return files.permission_ts("0.1.0")


def test_the_permission_step_is_its_golden(step):
    assert step == (DATA / "permission.ts").read_text(encoding="utf-8")
    assert step.splitlines()[0] == "// Liminal's permission step for Pi, v1 (plugin-platform-pi 0.1.0, for Pi 1.5.2)."
    assert all(len(line) <= 120 for line in step.splitlines())


def test_it_holds_every_tool_call_on_pis_tool_call_event_and_asks_on_pis_screen(step):
    """C-P1.1: pi.on("tool_call", handler), the handler awaited with no timeout; ctx.ui.confirm(title, message,
    {signal}); {block: true, reason} refuses the call."""
    assert step.count('pi.on("tool_call"') == 1 and "export default function liminalPermission(pi: any)" in step
    assert "await ctx.ui.confirm(" in step and "{ signal: ctx.signal }" in step
    assert step.count("block: true") == 3  # no screen, a command too long, declined
    assert "=== true" in step  # only a plain yes allows it: anything else, a throw among them, refuses
    assert "catch {\n      yes = false;" in step


def test_only_reads_and_liminals_own_mcp_tools_run_without_asking(step):
    assert files.READS == ("read", "grep", "find", "ls")
    assert 'const READS = new Set(["read", "grep", "find", "ls"]);' in step
    assert 'const DECIDED_ELSEWHERE = "mcp__liminal__";' in step
    assert "name.length > DECIDED_ELSEWHERE.length" in step  # the prefix alone is no tool of Liminal's
    for tool in ("bash", "powershell", "edit", "write"):  # never let through by a list
        assert f'"{tool}"' not in step.split("const READS")[1].split(";")[0]


def test_without_a_screen_every_call_it_asks_is_refused(step):
    """In Pi's print and json modes confirm answers false at once (C-P1.1): refused there, and wherever ctx has no
    confirm."""
    assert "if (!ctx || !ctx.hasUI || !ctx.ui || typeof ctx.ui.confirm !== \"function\")" in step
    assert "return { block: true, reason: NO_SCREEN };" in step


def test_a_shell_command_is_shown_whole_or_refused(step):
    assert f"const MOST = {files.SHOWN_MOST};" in step and files.SHOWN_MOST == 4000
    assert "if (command.length > MOST)" in step and "Split it into shorter commands." in step
    assert "cut(" not in step.split("if (SHELLS.has(name))")[1].split("} else {")[0]  # never cut


def test_what_is_asked_cannot_draw_over_its_own_question(step):
    """Control characters (escape, carriage return, backspace), the C1 range and the direction marks are shown as
    \\uXXXX; a line ending stays a line ending."""
    pattern = re.search(r"const odd = /\[(.*?)\]/g;", step).group(1)
    assert "return said.replace(odd, " in step
    shown = set()
    for low, high in re.findall(r"\\u([0-9a-f]{4})(?:-\\u([0-9a-f]{4}))?", pattern):
        shown.update(range(int(low, 16), int(high or low, 16) + 1))
    for char in (0x1B, 0x0D, 0x08, 0x00, 0x7F, 0x9B, 0x202E, 0x2066, 0x200F, 0xFEFF):
        assert char in shown, hex(char)
    assert 0x0A not in shown and 0x09 not in shown


def test_an_allowed_command_runs_without_liminals_token_and_key(step):
    assert 'const UNSET = ["LIMINAL_MCP_TOKEN", "LIMINAL_SERVER_KEY"];' in step
    assert 'event.input.command = "unset " + UNSET.join(" ") + "\\n" + event.input.command;' in step
    assert "Remove-Item -ErrorAction SilentlyContinue Env:" in step
    # the command is changed only after the answer: the decision comes before any change of its input (C-P1.1)
    assert step.index("await ctx.ui.confirm(") < step.index("event.input.command =")
    assert "without \" + UNSET.join(\" and \") + \" in its environment" in step  # said in the question


def test_the_permission_step_loads_nothing_and_reaches_nothing(step):
    for word in ("import ", "require(", "fetch(", "process.", "child_process", "eval(", "Function(", "pi.exec"):
        assert word not in step, word
    code = re.sub(r"//[^\n]*", "", step)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    code = re.sub(r"/\[.*?\]/g", "//", code)
    for opener, closer in ("()", "{}", "[]"):
        assert code.count(opener) == code.count(closer), opener


def test_its_constants_are_pis_own_words():
    assert constants.OFF == {"PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PI_SKIP_VERSION_CHECK": "1"}
    assert constants.KEY_SAID == "${LIMINAL_SERVER_KEY}" and constants.API == "openai-completions"
    assert constants.EXTENSION[:2] == ("pi", "liminal") and "extensions" not in constants.EXTENSION
