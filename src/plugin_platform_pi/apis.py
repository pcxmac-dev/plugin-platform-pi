"""What the Pi plugin attaches to (plugin API 2.2; the user, 2026-11-11: "each plugin should reflect the the API its
attached to, and present links that provide documentation ... it should also expose more of what the API is about"):
Pi's coding agent itself, the command it starts; its three configuration files and its permission step, which the
plugin writes; npm's registry, where Install has npm fetch Pi; and Node.js, the program Pi runs on. Each part of each
is named with what the plugin does with it, each call it makes with what it makes it for, and the notable calls it
does not make. The pages are the makers' own (Pi's documentation at the tag v1.5.2, its package on npm, Node.js's
release), read on 2026-11-18 (liminal_libs.sources.apis.dead_links checks them, LIMINAL_VENDOR_PAGES=1)."""
from __future__ import annotations

from liminal_libs.sources.apis import Api, Area, Call, Link

from .constants import NODE_FILES, NODE_VERSION, PACKAGE, PIN, RIPGREP, TAG

VERIFIED = "2026-11-18"
PI = "Pi coding agent"
CONFIG = "Pi configuration (models.json, mcp.json, settings.json)"
NPM = "npm registry"
NODE = "Node.js"

_REPO = "https://github.com/earendil-works/pi"
_DOCS = _REPO + "/blob/" + TAG + "/packages/coding-agent/"
_README = _DOCS + "README.md"
_MODELS = _DOCS + "docs/models.md"
_MCP = _DOCS + "docs/mcp.md"
_SECURITY = _DOCS + "docs/security.md"
_WINDOWS = _DOCS + "docs/windows.md"
_ENV = _DOCS + "docs/environment-variables.md"
_EXTENSIONS = _DOCS + "docs/extensions.md"
_SETTINGS = _DOCS + "docs/settings.md"
_GATE = _DOCS + "examples/extensions/permission-gate.ts"
_CHANGELOG = _DOCS + "CHANGELOG.md"
_PACKAGE = "https://www.npmjs.com/package/" + PACKAGE + "/v/" + PIN
_NODE_DOCS = "https://nodejs.org/docs/latest-v24.x/api/"
_RIPGREP = "https://github.com/BurntSushi/ripgrep/releases/tag/" + RIPGREP

PI_API = Api(
    name=PI, maker="earendil-works (Pi's authors)", kind="command",
    about=("Pi's coding agent, an open-source agent in the terminal: it reads the folder, runs shell commands and "
           "edits files through a model of a provider's, with extensions and MCP servers for more. It asks nothing "
           "before a tool call and has no sandbox, by its makers' design. The plugin starts its own pinned copy on its "
           "own Node.js in the folder you pick, against one model server's instance as its one provider, offline "
           "(no catalogue, version check, package install or download of its tools), with a permission step of the "
           "plugin's own that asks you before each command, edit and write."),
    base="pi (app/1.5.2/cli/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js, run by app/1.5.2/node)",
    version=f"{PIN}, the tag {TAG} of 2026-11-10",
    auth=("none of its own toward the model server but the server's key, where one is kept, handed over in its "
          "environment (LIMINAL_SERVER_KEY, which its provider's apiKey names)"),
    limits=("its context is the one models.json gives the model; an MCP server's call waits the MCP plugin's hold and "
            "a minute more"),
    costs="free (MIT); a hosted provider it can use may be paid, and none is given from here",
    links=(
        Link("Pi's README", _README, "docs"),
        Link("Models and providers", _MODELS, "reference"),
        Link("MCP in Pi", _MCP, "guide"),
        Link("Security", _SECURITY, "guide"),
        Link("Pi on Windows", _WINDOWS, "guide"),
        Link("Environment variables", _ENV, "reference"),
        Link("Extensions", _EXTENSIONS, "reference"),
        Link("The permission gate example", _GATE, "guide"),
        Link("Its changes", _CHANGELOG, "changelog"),
        Link("earendil-works/pi", _REPO, "source"),
        Link("Its licence (MIT)", _REPO + "/blob/" + TAG + "/LICENSE", "terms"),
    ),
    areas=(
        Area("Its terminal screen", "pi: a session in the terminal, in the folder it is started in", _README,
             covered=("started in the folder you pick, in a window of its own or by the lines you paste, with the "
                      "permission step, its one provider and the model on its command line")),
        Area("Its tools", "read, bash, edit and write by default; grep, find, ls and powershell when asked", _README,
             covered=("each call that is not a read asked of you first by the plugin's permission step; --no-tools "
                      "where Use… says the model calls none")),
        Area("Extensions", "TypeScript modules it loads: -e, its agent folder's, a trusted folder's .pi/extensions",
             _EXTENSIONS,
             covered=("one of the plugin's own, its permission step on the tool_call event (ctx.ui.confirm, then "
                      "block or run); no folder's own")),
        Area("MCP servers", "the servers of its mcp.json (stdio, streamable HTTP)", _MCP,
             covered="Liminal's MCP alone, through the MCP plugin's bridge, where Use… turns it on"),
        Area("Project trust", "a folder's .pi/ (settings, MCP servers, extensions), loaded only once trusted",
             _SECURITY, covered="never trusted from here (defaultProjectTrust: never)"),
        Area("Context files", "AGENTS.md and CLAUDE.md of the folder, every folder above it and its agent folder",
             _SECURITY),
        Area("What it reaches by itself", "its model catalogue, its version check, its install ping, its packages, its "
                                          "fd and ripgrep downloads", _ENV,
             covered="all off: PI_OFFLINE=1, PI_TELEMETRY=0, PI_SKIP_VERSION_CHECK=1, its tools placed beforehand"),
        Area("Sessions", "each session's transcript in its sessions folder", _README,
             covered="its own folder; the newest 100 kept (200 MB at the most), older ones removed at Open…"),
        Area("Sharing and sign-in", "/share (a GitHub gist), /bug, /login to a hosted provider", _README),
    ),
    calls=(
        Call("node cli.js -e permission.ts --provider liminal --model MODEL", "its terminal screen in the working "
                                                                              "folder", "Its terminal screen",
             used="what Open… starts, in the folder you pick (Command… shows the same lines)", docs=_README,
             writes=True),
        Call("tool_call (an extension's event)", "a tool call held until the handler answers: run, or blocked with "
                                                 "a reason", "Extensions",
             used="by the plugin's permission step, for every call that is not a read", docs=_EXTENSIONS),
        Call("--no-context-files", "no AGENTS.md or CLAUDE.md loaded, its agent folder's among them", "Context files",
             docs=_SECURITY),
        Call("/share", "the session sent to a GitHub gist through gh", "Sharing and sign-in", docs=_README,
             writes=True),
        Call("/login", "a sign-in to a hosted provider, its credentials kept", "Sharing and sign-in", docs=_README,
             writes=True),
        Call("pi install npm:PACKAGE", "a Pi package installed by npm", "Extensions", docs=_README, writes=True),
    ),
    verified=VERIFIED,
)

CONFIG_API = Api(
    name=CONFIG, maker="earendil-works (Pi's authors)", kind="file",
    about=("Pi's configuration in its agent folder (PI_CODING_AGENT_DIR): models.json, its providers and their models; "
           "mcp.json, its MCP servers; settings.json, its settings. The plugin writes the three whole at every start "
           "in its own agent folder, with its permission step beside them: one provider (liminal), Liminal's MCP "
           "alone or no server, every folder untrusted, its install ping off, on Windows its shell by its whole path. "
           "A value beginning with ! would be run as a command, and none is ever written."),
    base="<the plugin's folder>/config/pi/agent/",
    version=f"Pi {PIN}'s",
    auth="none: files of the plugin's own",
    limits="none",
    costs="free",
    links=(
        Link("Models and providers", _MODELS, "reference"),
        Link("MCP in Pi", _MCP, "guide"),
        Link("Settings", _SETTINGS, "reference"),
    ),
    areas=(
        Area("models.json", "providers: baseUrl, api, apiKey ($NAME, a literal or !command), headers, models",
             _MODELS, covered="providers.liminal alone, its apiKey ${LIMINAL_SERVER_KEY} or the literal none"),
        Area("mcp.json", "mcpServers: command, args, env and headers ($NAME resolved), timeout", _MCP,
             covered="Liminal's MCP through the bridge, its env naming LIMINAL_MCP_TOKEN, or no server"),
        Area("settings.json", "defaultProjectTrust, shellPath, enableInstallTelemetry, packages, extensions", _SETTINGS,
             covered="defaultProjectTrust never, enableInstallTelemetry false, shellPath on Windows; no packages"),
    ),
    calls=(
        Call("write models.json, mcp.json, settings.json, permission.ts", "each written whole, a part file renamed",
             "settings.json", used="at every start, before Pi reads them", writes=True),
    ),
    verified=VERIFIED,
)

NPM_API = Api(
    name=NPM, maker="npm, Inc. (GitHub)", kind="feed",
    about=("Where Install has npm fetch Pi: @earendil-works/pi-coding-agent at its exact version, its sha512 pinned in "
           "the plugin and compared with the one npm's lock records before anything is put in use, its dependencies "
           "resolved by npm and checked against the registry's own sums. npm runs with no script, no audit, no "
           "update notice, none of your npm settings and an empty npmrc; its lock is kept for a repair."),
    base="https://registry.npmjs.org/",
    version=f"{PACKAGE} {PIN}",
    auth="none: public packages",
    limits="none named; asked only when you click Install… or Update…",
    costs="free",
    links=(
        Link(f"{PACKAGE} {PIN} on npm", _PACKAGE, "docs"),
        Link("npm install", "https://docs.npmjs.com/cli/v11/commands/npm-install", "reference"),
        Link("npm ci", "https://docs.npmjs.com/cli/v11/commands/npm-ci", "reference"),
    ),
    areas=(
        Area("Its package", "the package, its tarball and its dist.integrity", _PACKAGE,
             covered="installed at 1.5.2 by npm, its sha512 compared with the pin"),
        Area("Its dependencies", "22 exact versions in its package.json, theirs resolved on the day", _PACKAGE,
             covered="checked by npm against the registry's own sums; not pinned in this plugin"),
    ),
    calls=(
        Call(f"npm install --prefix cli --save-exact --ignore-scripts {PACKAGE}@{PIN}", "Pi and what it needs, into "
                                                                                       "the install's own folder",
             "Its package", used="Install, as a job", writes=True),
        Call("npm ci --prefix cli --ignore-scripts", "exactly the packages of the kept lock again", "Its dependencies",
             used="a repair or a reinstall of the same pin", writes=True),
    ),
    verified=VERIFIED,
)

NODE_API = Api(
    name=NODE, maker="the OpenJS Foundation", kind="command",
    about=(f"The JavaScript runtime Pi runs on: Node.js {NODE_VERSION} of the plugin's own (its long-term line, 24), "
           "never one of yours, its archive pinned by size and sha256. Pi is started as that node with its "
           "dist/bundle/cli.js, by their whole paths; its compiled code is cached in the plugin's folder."),
    base="app/1.5.2/node (node.exe on Windows, bin/node on Linux)",
    version=NODE_VERSION,
    auth="none",
    limits="none",
    costs="free (MIT)",
    links=(
        Link(f"Node.js {NODE_VERSION}: its archives and SHASUMS256.txt", NODE_FILES, "tool"),
        Link("Node.js 24's documentation", _NODE_DOCS, "docs"),
        Link("Its compile cache (NODE_COMPILE_CACHE)", _NODE_DOCS + "module.html", "reference"),
        Link(f"ripgrep {RIPGREP}, placed beside it for Pi", _RIPGREP, "tool"),
    ),
    areas=(
        Area("Its archive", "node-v<version>-<system>-<arch>.zip | .tar.xz from nodejs.org", NODE_FILES,
             covered="downloaded at Install, checked against its pinned size and sha256 (none pinned in 0.1.0)"),
        Area("npm", "npm-cli.js, which comes with it", "https://docs.npmjs.com/cli/v11",
             covered="run by that node by its whole path, never npm.cmd or an npm on PATH"),
    ),
    calls=(
        Call(f"GET {NODE_FILES}node-v{NODE_VERSION}-<target>.zip | .tar.xz", "Node.js's archive for this system",
             "Its archive", used="Install and Update, as a job"),
    ),
    verified=VERIFIED,
)

APIS = (PI_API, CONFIG_API, NPM_API, NODE_API)
