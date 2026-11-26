"""What it says of the interface it shares, as the Internal API tab reads it (liminal_libs.internal, from the library
release that carries it): sound, its kind and its bases' standard interface, what it keeps and what it asks, the MCP
plugin's four among them."""
from __future__ import annotations

from liminal_libs import internal

import plugin_platform_pi as module


def test_the_internal_api_tab_finds_nothing_wrong():
    assert internal.problems(module.MACHINE) == []


def test_it_is_harness_middleware_and_says_what_it_keeps_and_asks():
    page = internal.internal_of(module.MACHINE)
    assert [s["class"] for s in page["standard"]][:2] == ["Harness", "AiPlugin"]
    assert [k["variable"] for k in page["keeps"]] == ["LIMINAL_AI_PI_USE"]
    assert [(a["plugin"], a["hook"]) for a in page["asks"]] == [
        ("", "serving"), ("", "models_of"), ("mcp", "client_offer"), ("mcp", "ensure_client"),
        ("mcp", "launch_token"), ("mcp", "end_launch")]
    kinds = {h["name"]: h["kind"] for h in page["hooks"]}
    assert kinds["open"] == "change" and kinds["command"] == "read" and kinds["install"] == "job"
    assert kinds["use"] == "change" and kinds["ask_models"] == "read"
