"""The plugin conforms to the class contract (plugin API 2.2): liminal_libs.sources.conformance, read from the plugin
alone (nothing runs). A harness of the platform's AI plugins, drawn under AI plugins, Harnesses, at 524; its icon Pi's
own mark, drawn by the library; its hooks the harness base's and no other; Liminal's MCP offered by the bridge alone;
what it says of the interface it shares; one run state for the registry's copies; its versions and its floor as
pyproject says them."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

import liminal_libs
import plugin_platform_pi as module
from liminal_libs.machines import harness
from liminal_libs.machines.ai import AiPlugin
from liminal_libs.machines.harness import Harness
from liminal_libs.sources.conformance import assert_module_conforms
from liminal_libs.ui import STATIC

HERE = Path(__file__).resolve().parent.parent
PYPROJECT = tomllib.loads((HERE / "pyproject.toml").read_text(encoding="utf-8"))


def release(version: str) -> tuple[int, ...]:
    """A release's number as a tuple ("1.66.0" -> (1, 66, 0)), what follows its digits left out."""
    return tuple(int(re.match(r"\d*", part).group() or 0) for part in str(version).split(".")[:3])


def test_it_conforms_to_the_class_contract():
    found = assert_module_conforms(module)
    assert [p.name for p in found] == ["pi"] and all(p.api == "2.2" and not p.is_record for p in found)
    assert {p.SYSTEM for p in found} == {"platform"} and {p.KIND for p in found} == {"machine"}
    assert all(p.apis and p.interface()["apis"] == [a.name for a in p.apis] for p in found)
    p = module.MACHINE
    assert isinstance(p, Harness) and isinstance(p, AiPlugin) and p.title == "Pi"
    assert p.about.startswith("Pi's open-source coding agent") and len(p.about) <= 120


def test_it_is_drawn_under_ai_plugins_harnesses_at_524():
    """Its section and group (liminal-libs 1.62.0): AI plugins, Harnesses, at 524, after OpenCode 520, Aider 521,
    Continue 522 and Codex CLI 523, before goose 525 (the plan of 2026-11-18)."""
    p = module.MACHINE
    assert (p.SECTION, p.GROUP, p.order) == ("ai", "harness", 524)


def test_its_icon_is_pis_own_mark_drawn_by_the_library():
    """Pi's own mark, in liminal-libs 1.66.0's icons.js: a mark missing, or drawn under another name, fails it."""
    assert module.MACHINE.ICON == "pi"
    drawn = set(re.findall(r"^\s*([a-z]+):\s*'", (STATIC / "icons.js").read_text(encoding="utf-8"), re.M))
    assert "pi" in drawn, f"liminal-libs {liminal_libs.__version__} draws no pi mark"


def test_its_hooks_are_the_harness_bases_and_no_other():
    p = module.MACHINE
    hooks = p.interface()["hooks"]
    assert set(hooks) == {"present", "status", "refresh", "install", "uninstall", "use", "open", "command",
                          "ask_models"}
    assert p.HOOKS == Harness.HOOKS and "terminal" not in hooks
    assert p.JOB_HOOKS == ("install",) and p.CANCEL_HOOKS == ("install",)
    assert not p.gives("check") and p.STEPS == () and not p.gives("setup")  # the page asks Install at once
    assert hooks["open"] == "(folder=None) -> 'dict'"
    assert getattr(module.PiPlugin.open, "held", False)  # waits for no install: AiPlugin's START_HOOKS


def test_its_changes_are_asked_from_the_page_alone():
    """liminal-libs 1.99.0: a harness's changes are page-only, the base's four; it adds no change hook of its own, so
    it names none (PAGE_ONLY_HOOKS). Its permission step asks on Pi's own screen: no hook of the platform's."""
    assert "PAGE_ONLY_HOOKS" not in module.PiPlugin.__dict__
    assert set(module.MACHINE.PAGE_ONLY_HOOKS) >= {"install", "uninstall", "use", "open"}


def test_its_options_and_liminals_mcp():
    p = module.MACHINE
    assert [s.name for s in p.OPTIONS] == ["context", "tools", "mcp"]
    assert p.OPTIONS[-1] is harness.MCP_OPTION and p.MCP_WIRES == ("stdio",)
    tools = p.OPTIONS[1]
    assert tools.default == "auto" and [c[0] for c in tools.choices] == ["auto", "yes", "no"]
    context = p.OPTIONS[0]
    assert (context.min, context.max) == (8192, 2_000_000)
    assert not any(s.name in ("permission", "ask", "approve") for s in p.OPTIONS)  # its permission step, always
    assert set(Harness.OPENERS) < set(p.OPENERS) and "$" in p.OPENERS  # Pi resolves $NAME too


def test_what_it_says_of_the_interface_it_shares():
    """The Internal API tab's words (read by name; every plugin is middleware): a harness with no hook of its own, so
    no read of its own and no service; what it asks of the other plugins (the model servers and the MCP plugin) and
    what it keeps through the login are the base's."""
    p = module.MACHINE
    assert module.PiPlugin.__dict__["READ_HOOKS"] == () and module.PiPlugin.__dict__["SERVICE_HOOKS"] == ()
    assert "KEEPS" not in module.PiPlugin.__dict__
    assert [ask[:2] for ask in p.ASKS] == [("", "serving"), ("", "models_of"), ("mcp", "client_offer"),
                                           ("mcp", "ensure_client"), ("mcp", "launch_token"), ("mcp", "end_launch")]
    assert p.variable("use") == "LIMINAL_AI_PI_USE"
    assert all(isinstance(n, str) and 0 < len(n) <= 400 for n in p.INTERNAL_NOTES)
    assert set(harness.MCP_NOTES) <= set(p.INTERNAL_NOTES)
    for hook in ("use", "open", "command", "status"):
        assert (getattr(module.PiPlugin, hook).__doc__ or "").strip(), hook


def test_a_copy_the_registry_hands_out_shares_what_the_plugin_keeps():
    p = module.PiPlugin()
    copy = p.with_(origin="the plugin directory's checkout")
    assert copy is not p and copy._rt is p._rt and copy.out is p.out
    assert type(p._rt).__name__ == "PiRun"


def test_its_versions_and_its_floor_are_pyprojects():
    project = PYPROJECT["project"]
    assert module.__version__ == project["version"] == "0.1.1"
    assert project["dependencies"] == ["liminal-libs>=1.99.0"]
    assert module.LIBS_FLOOR == module.MACHINE.LIBS_FLOOR == "1.99.0"  # the base's changes page-only
    assert project["entry-points"]["liminal.providers"] == {"pi": "plugin_platform_pi"}
    assert release(liminal_libs.__version__) >= release(module.LIBS_FLOOR)
    assert module.MACHINE.too_old() == ""
    changelog = (HERE / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(r"^## (\S+) \((\S+)\)", changelog, re.M).groups() == (module.__version__, "2026-11-27")


def test_a_library_older_than_its_floor_is_said_and_refuses_every_hook(monkeypatch, tmp_path):
    """Below 1.99.0 its base's changes can be asked by any program (below 1.66.0 there is no machines/node.py
    either): the page says so, and nothing runs."""
    from conftest import made, refused

    p = made(tmp_path)
    monkeypatch.setattr(liminal_libs, "__version__", "1.98.2")
    assert p.too_old() == "Pi needs liminal-libs 1.99.0 or newer, and this is 1.98.2: update the library"
    status = p.status()
    assert status["valid"] is False and status["why"] == p.too_old()
    assert refused(lambda: p.ask("install", True)) == p.too_old()
