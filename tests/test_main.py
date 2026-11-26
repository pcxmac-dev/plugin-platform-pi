"""The command line (`python -m plugin_platform_pi`), its reads alone: its Main as JSON; Command… without the platform
said in words; anything else its usage, install and uninstall among them (liminal-libs 1.99.0: a harness's changes
are asked from its page). The module's plugin is a stand-in's for each test: nothing is installed, downloaded or
started."""
from __future__ import annotations

import json

import pytest

import plugin_platform_pi as plugin
from conftest import installed, made
from plugin_platform_pi import __main__ as cli


@pytest.fixture
def alone(tmp_path, monkeypatch):
    """The module's plugin, on stand-ins and not attached to the platform (as on a command line)."""
    p = made(tmp_path, "windows", app=False)
    monkeypatch.setattr(cli, "MACHINE", p)
    return p


def test_status_prints_its_main_as_json(alone, capsys):
    assert cli.main(["status"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["valid"] is True and status["summary"] == "not installed"
    assert status["pinned"] == "Pi 1.5.2 on Node.js 24.22.3 (node-v24.22.3-win-x64.zip)"
    assert cli.main([]) == 0  # status is the default


def test_command_without_the_platform_is_said_in_words(alone, capsys, tmp_path):
    installed(alone)
    assert cli.main(["command", str(tmp_path)]) == 1
    assert "choose a model server first: Use…" in capsys.readouterr().err


def test_its_changes_are_not_offered_here(alone, capsys):
    for words in (["install", "--force"], ["uninstall", "--force"], ["open"], ["status", "extra"]):
        assert cli.main(words) == 2
    assert capsys.readouterr().err.count(cli.USAGE) == 4
    assert not (alone.home / "app").exists() and not (alone.home / "downloads").exists()
    assert plugin.MACHINE is not alone  # (the module's own plugin, untouched)
