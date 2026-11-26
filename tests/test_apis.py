"""What the plugin attaches to (plugin API 2.2): its four cards are sound; each call belongs to one of its card's parts;
every page they link is on its maker's own host; the calls they say the plugin makes are exactly the addresses an
install asked, the npm command it ran and the command a start ran, read from the stand-ins as the plugin sent them;
nothing costs. With LIMINAL_VENDOR_PAGES=1 alone, every address on them is asked (the only test here that reaches the
network)."""
from __future__ import annotations

import os
import urllib.parse

import pytest

import plugin_platform_pi as plugin
from conftest import Npm, chosen, made, rg_pin, Web
from liminal_libs.machines import node
from liminal_libs.machines.terminal import Output
from liminal_libs.sources import apis as A
from plugin_platform_pi import apis as cards
from plugin_platform_pi import constants


def test_its_cards_are_sound():
    assert A.problems(cards.APIS) == [] and plugin.MACHINE.apis is cards.APIS
    assert [a.name for a in cards.APIS] == ["Pi coding agent", "Pi configuration (models.json, mcp.json, "
                                            "settings.json)", "npm registry", "Node.js"]
    assert [a.kind for a in cards.APIS] == ["command", "file", "feed", "command"]
    for api in cards.APIS:
        assert api.verified == cards.VERIFIED == "2026-11-18" and api.docs.startswith("https://")
        assert all(c.area in {x.name for x in api.areas} for c in api.calls), api.name
        assert api.used and api.covered
    pi = cards.PI_API
    assert len(pi.areas) > len(pi.covered) and len(pi.calls) > len(pi.used)  # more than it uses
    assert not any(c.costs for a in cards.APIS for c in a.calls)
    assert {c.name for c in pi.calls if not c.used} == {"--no-context-files", "/share", "/login",
                                                        "pi install npm:PACKAGE"}
    assert "asks nothing before a tool call and has no sandbox" in pi.about


def test_every_page_they_link_is_its_makers_own():
    for api in cards.APIS:
        for url in A.urls((api,)):
            assert urllib.parse.urlsplit(url).hostname in (*constants.MAKERS, "docs.npmjs.com"), url
    links = {x.url for x in cards.PI_API.links}
    base = "https:" + "//github.com/earendil-works/pi/blob/v1.5.2/packages/coding-agent/"
    for doc in ("README.md", "docs/models.md", "docs/mcp.md", "docs/security.md", "docs/windows.md",
                "docs/environment-variables.md", "docs/extensions.md", "examples/extensions/permission-gate.ts"):
        assert base + doc in links, doc


@pytest.mark.parametrize("system", ["windows", "linux"])
def test_the_calls_it_says_it_makes_are_the_ones_it_makes(tmp_path, monkeypatch, node_pins, system):
    npm = Npm()
    p = made(tmp_path, system, streamer=npm, interactive=True)
    name = node.archive("24.22.3", system, p.machine_word())
    rg_url, rg_data = rg_pin(monkeypatch, system)
    p.out.opener = web = Web({constants.NODE_FILES + name: node_pins[name], rg_url: rg_data})
    assert p.install(True, log=Output())["ok"] is True
    asked = [urllib.parse.urlsplit(url) for url in web.asked]
    assert [(u.hostname, u.path.rsplit("/", 1)[0]) for u in asked] == [
        ("nodejs.org", "/dist/v24.22.3"), ("github.com", "/BurntSushi/ripgrep/releases/download/15.1.0")]
    assert {c.name for c in cards.NODE_API.used} == {"GET https://nodejs.org/dist/v24.22.3/node-v24.22.3-<target>.zip "
                                                     "| .tar.xz"}
    [ran] = npm.ran
    assert ran["argv"][2:4] == ["install", "--prefix"] and "--ignore-scripts" in ran["argv"]
    assert {c.name for c in cards.NPM_API.used} == {
        "npm install --prefix cli --save-exact --ignore-scripts @earendil-works/pi-coding-agent@1.5.2",
        "npm ci --prefix cli --ignore-scripts"}
    project = tmp_path / "project"
    project.mkdir()
    chosen(p)
    launch = p._launch(str(project), p.use_kept(), p.serving_of("ollama/default"), "")
    assert os.path.basename(launch.argv[1]) == "cli.js" and launch.argv[2:6] == ("-e", str(p.extension_path()),
                                                                                  "--provider", "liminal")
    assert "node cli.js -e permission.ts --provider liminal --model MODEL" in {c.name for c in cards.PI_API.used}
    for name in ("models.json", "mcp.json", "settings.json"):
        assert (p.agent_dir() / name).is_file()
    assert p.extension_path().is_file()


def test_its_hosts_are_the_ones_install_may_be_sent_to():
    hosts = {urllib.parse.urlsplit(u).hostname for u in (constants.NODE_FILES, constants.RIPGREP_FILES,
                                                          constants.REGISTRY)}
    assert hosts | set(constants.ASSET_HOSTS) == set(constants.HOSTS)


@pytest.mark.skipif(os.environ.get("LIMINAL_VENDOR_PAGES") != "1",
                    reason="reaches the makers' pages: LIMINAL_VENDOR_PAGES=1")
def test_every_address_on_its_cards_answers(monkeypatch):
    monkeypatch.undo()  # this test alone reaches the network (conftest refuses it to every other)
    assert A.dead_links(cards.APIS) == []
