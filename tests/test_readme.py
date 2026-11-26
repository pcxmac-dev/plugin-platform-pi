"""What the README and the CHANGELOG tell the user, where the plugin's behaviour rests on their words (the behaviour
itself is tested beside the code): what only a real run confirms is listed; its permission step, its ports and its
context files said plainly (the user's answers 7 and 8); its shell on Windows and WSL's launcher never; the install's
pins and its hosts, and that Node.js is not pinned in this release. Read as text, nothing run."""
from __future__ import annotations

import re
from pathlib import Path

from plugin_platform_pi import constants

HERE = Path(__file__).resolve().parent.parent


def words(name: str) -> str:
    """A file's text with its line breaks and runs of spaces as one space, as it reads."""
    return re.sub(r"\s+", " ", (HERE / name).read_text(encoding="utf-8"))


def section(name: str, title: str) -> str:
    """One section of a file (from its "## title" to the next "## "), as it reads."""
    text = (HERE / name).read_text(encoding="utf-8")
    start = text.index(f"\n## {title}\n")
    end = text.find("\n## ", start + 1)
    return re.sub(r"\s+", " ", text[start:end if end > 0 else None])


def test_the_readme_lists_what_only_a_real_run_confirms():
    said = section("README.md", "Not yet confirmed by a real run")
    for item in ("Node.js 24.22.3's archives", "`npm ci` from the kept lock", "`contextWindow`", "`--no-tools`",
                 "loaded by `-e` as TypeScript", "MCP tools reach the `tool_call` event", "`where.exe`",
                 "ripgrep found in the agent folder's `bin/`", "revision 2025-11-25", "WSLg"):
        assert item in said, item


def test_the_readme_says_its_permission_step_its_ports_and_its_context_files_plainly():
    said = words("README.md")
    assert "asks nothing before a tool call and has no sandbox, by its makers' design" in said
    assert "before each call that is not a read" in said and "longer than 4,000 characters" in said
    assert "What you allow runs at once with your rights, with no sandbox" in said
    assert "none opened by itself here" in said and "loopback while it lasts" in said
    assert "`--no-context-files`" in said and "it is not passed from here" in said
    assert "/share and /bug" in said and "Nothing does so by itself." in said


def test_the_readme_says_its_shell_and_wsls_launcher_never():
    said = words("README.md")
    for item in ("Git for Windows' bash", "`%LOCALAPPDATA%\\Programs\\Git\\bin`", "installing Git for Windows is yours",
                 "it is never used from here, even first on PATH", "`NoDefaultCurrentDirectoryInExePath=1`"):
        assert item in said, item
    for name in constants.PLANTED:
        assert f"`{name}`" in said, name


def test_the_readme_says_how_the_install_is_pinned_and_from_where():
    said = words("README.md")
    assert all(host.replace(".", ".") in said for host in constants.HOSTS)
    assert "**None is pinned in this release**" in said and "`SHASUMS256.txt`" in said
    assert "--ignore-scripts" in said and "none of them is pinned in this plugin" in said
    assert "fd (Pi's `@` completion and its find tool, off unless asked) is not pinned in this release" in said


def test_the_changelog_names_its_release_and_the_users_words():
    changelog = words("CHANGELOG.md")
    assert changelog.startswith("# Changelog ## 0.1.0 (2026-11-26)")
    assert ('"kept, with the plugin\'s own permission step before every shell command, edit and write"' in changelog
            and "Needs liminal-libs>=1.66.0." in changelog)


def test_no_line_is_longer_than_120_characters():
    paths = [*HERE.rglob("*.py"), *HERE.rglob("*.md"), *HERE.rglob("*.toml"), *HERE.rglob("*.yml"),
             *HERE.rglob("*.ts")]
    for path in sorted(paths):
        if any(part in (".git", "__pycache__") for part in path.parts):
            continue
        long = [n for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if len(line) > 120]
        assert long == [], f"{path.relative_to(HERE)}: lines {long}"


def test_no_module_imports_what_it_does_not_use():
    for path in sorted([*(HERE / "src" / "plugin_platform_pi").glob("*.py"), *(HERE / "tests").glob("*.py")]):
        text = path.read_text(encoding="utf-8")
        names = re.findall(r"^from \S+ import \(?([^)]+?)\)?$", text, re.M | re.S)
        imported = [n.strip().split(" as ")[-1] for line in names for n in line.split(",") if n.strip()]
        imported += re.findall(r"^import (\w+)$", text, re.M)
        body = re.sub(r"^(from \S+ import \([^)]*\)|from .*|import .*)$", "", text, flags=re.M)
        unused = [n for n in imported if n != "annotations" and not re.search(rf"\b{re.escape(n)}\b", body)]
        assert unused == [], f"{path.name}: {unused}"
