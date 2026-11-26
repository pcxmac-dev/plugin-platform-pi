"""What the Pi plugin pins and every outside address it names (the library names none: A-revisions 0).

The pins are read from what Pi's makers publish about their release, never from a download (A-revisions 3), on
2026-11-18 (the pre-build checks, C-P1): npm's record of @earendil-works/pi-coding-agent 1.5.2 (registry.npmjs.org)
and its SLSA provenance, which names the tag v1.5.2 and its commit; the sources read at that commit.

- Pi's coding agent 1.5.2 (npm's `latest` tag, published 2026-11-10): its sha512 as npm's dist.integrity gives it,
  compared with the one npm's lock records once npm installed it (liminal_libs.machines.node.checked). Its 22
  dependencies are exact versions in its package.json; npm resolves their own dependencies from the registry on the
  day, each checked against the registry's own sum, none of them pinned here. Its bin is `pi`, dist/bundle/cli.js.
- Node.js 24, Pi's own copy: Pi needs 22.19 or newer, and the same line serves the MCP plugin's Node.js servers.
  24.22.3 is the newest of the line C-P1 read (2026-11-10). Its archives' sizes and sha256 (nodejs.org's
  SHASUMS256.txt) were not read before this release was built, so none is pinned (NODE_BUILDS is empty) and Install
  says so: reading them is a page read the user says yes to.
- ripgrep 15.1.0, which Pi's grep tool and its bash commands run, placed where Pi looks before it would look on PATH
  or download the newest from GitHub unchecked (C-P1.3a): the builds and sums plugin-platform-opencode pins (read
  from ripgrep's release, equal to OpenCode 2.3.0's pins). fd, for Pi's @ completion and its find tool (off by
  default), is not pinned in this release: its sums were not read.

What Pi is given at a start is read in its sources at the tag (packages/coding-agent/), each step named where it is
used (files.py, the plugin's launch)."""
from __future__ import annotations

import re

# -- Pi ----------------------------------------------------------------------------------------------------------------
PACKAGE = "@earendil-works/pi-coding-agent"
PIN = "1.5.2"  # a pin moves only with a release of this plugin
TAG = "v1.5.2"
COMMIT = "b4afdddf44e059c67ccf5097e5317d913521b470"  # the tag's, as npm's provenance names it
RELEASED = "2026-11-10"
INTEGRITY = ("sha512-mUWI04rqF1Vd/m1q+Ps1XeWsTXEVvRUnsmRa83I3Dzua0Tx5bYS93imeqtIfrXf7PkkaR6ERz+AuQhIJlom5yA==")
UNPACKED = 24_401_012  # npm's unpackedSize: the tarball's own size is not in its record
LICENCE = "Pi: MIT (its authors, earendil-works/pi). Node.js: MIT and the licences its LICENSE file names."
BIN = "pi"  # its package.json's bin: {"pi": "dist/bundle/cli.js"}
REGISTRY = "https://registry.npmjs.org/"
REPOSITORY = "earendil-works/pi"

# -- its Node.js -------------------------------------------------------------------------------------------------------
NODE_VERSION = "24.22.3"
NODE_FILES = "https://nodejs.org/dist/v24.22.3/"
# by (system, arch), node.archive's names: (archive, bytes, sha256), from SHASUMS256.txt and the files' own sizes.
# Not read before this release: empty, so Install is refused in words until a release pins them.
NODE_BUILDS: dict[tuple[str, str], tuple[str, int, str]] = {}

# -- what Pi runs for its searches -------------------------------------------------------------------------------------
RIPGREP = "15.1.0"
RIPGREP_FILES = "https://github.com/BurntSushi/ripgrep/releases/download/15.1.0/"
RIPGREP_LICENCE = "ripgrep 15.1.0: Unlicense or MIT (Andrew Gallant)."
# by (system, arch), as plugin-platform-opencode 0.1.0 pins them: (archive, bytes, sha256); each holds
# ripgrep-15.1.0-<platform>/ with the program in it
RIPGREP_BUILDS: dict[tuple[str, str], tuple[str, int, str]] = {
    ("windows", "x64"): ("ripgrep-15.1.0-x86_64-pc-windows-msvc.zip", 1810687,
                         "124510b94b6baa3380d051fdf4650eaa80a302c876d611e9dba0b2e18d87493a"),
    ("windows", "arm64"): ("ripgrep-15.1.0-aarch64-pc-windows-msvc.zip", 1675460,
                           "00d931fb5237c9696ca49308818edb76d8eb6fc132761cb2a1bd616b2df02f8e"),
    ("linux", "x64"): ("ripgrep-15.1.0-x86_64-unknown-linux-musl.tar.gz", 2263077,
                       "1c9297be4a084eea7ecaedf93eb03d058d6faae29bbc57ecdaf5063921491599"),
    ("linux", "arm64"): ("ripgrep-15.1.0-aarch64-unknown-linux-gnu.tar.gz", 1869959,
                         "2b661c6ef508e902f388e9098d9c4c5aca72c87b55922d94abdba830b4dc885e"),
}
FD = ""  # fd's version: not pinned in this release
FD_FILES = "https://github.com/sharkdp/fd/releases/download/"
FD_BUILDS: dict[tuple[str, str], tuple[str, int, str]] = {}
TOOLS = {"rg": {"windows": "rg.exe", "linux": "rg"}, "fd": {"windows": "fd.exe", "linux": "fd"}}
ASSET_HOSTS = ("release-assets.githubusercontent.com",)  # where github.com sends a release's file on to
HOSTS = ("nodejs.org", "registry.npmjs.org", "github.com", "release-assets.githubusercontent.com")
MAKERS = ("github.com", "www.npmjs.com", "nodejs.org")  # the hosts of the pages its cards link (never fetched)
# what its processor is called, by what Python says (platform.machine()), in Node.js's words
ARCHES = {"amd64": "x64", "x86_64": "x64", "x64": "x64", "em64t": "x64", "arm64": "arm64", "aarch64": "arm64"}

# -- where it keeps what it keeps --------------------------------------------------------------------------------------
# <home>/config/pi: agent/ is PI_CODING_AGENT_DIR (models.json, mcp.json and settings.json, written at each start;
# bin/ with the tools placed there; what Pi keeps itself: auth.json, its caches), sessions/ PI_CODING_AGENT_SESSION_DIR
# (each session's transcript, .jsonl), liminal/ the permission step (never in agent/extensions/, which Pi would load a
# second time), compile-cache/ Node.js's compiled code (NODE_COMPILE_CACHE: nothing in the temporary folder)
AGENT = ("pi", "agent")
SESSIONS = ("pi", "sessions")
EXTENSION = ("pi", "liminal", "permission.ts")
COMPILE_CACHE = ("pi", "compile-cache")
SESSION = re.compile(r"\.jsonl$")
SESSIONS_KEPT = 100  # the newest sessions kept at each Open… (the plan: "pruned at each Open...")
SESSIONS_BYTES = 200_000_000  # and no more than this many bytes of them, the newest first
SESSIONS_LOOKED = 100_000  # files looked at, at the most, in one pruning
# what of Pi's own settings.json survives the plugin's writing it whole: its note of the changelog it last showed
KEPT_SETTINGS = ("lastChangelogVersion",)

# -- what Pi is given --------------------------------------------------------------------------------------------------
PROVIDER = "liminal"  # its one custom provider, the model server's instance (models.json providers.liminal)
API = "openai-completions"  # Pi's word for an OpenAI-compatible chat completions server
SECRET = "LIMINAL_SERVER_KEY"  # the one variable a kept key reaches Pi by (its provider's apiKey names it)
KEY_SAID = "${" + SECRET + "}"
NO_KEY = "none"  # a literal key for a server that takes none (Pi reads a bare word as itself)
MCP_SECRET = "LIMINAL_MCP_TOKEN"  # the variable Liminal's MCP's token reaches it by (its mcp.json entry's env)
MCP_NAME = "liminal"  # the name Liminal's MCP is given among its MCP servers (its tools: mcp__liminal__*)
FEWEST = 8_192  # the least context Pi is started with
MOST = 2_000_000  # the most context typed under Use…
OUTPUT = 8_192  # the most output named to Pi (a quarter of its context, at most this)
OFF = {"PI_OFFLINE": "1", "PI_TELEMETRY": "0", "PI_SKIP_VERSION_CHECK": "1"}  # exactly these values (C-P1.3)
# Windows: a bare name is looked up on PATH alone, not first in the folder Pi runs in (libuv and cmd.exe read it by
# its presence; cross-spawn ignores it, so `planted` refuses such a folder all the same)
NO_FOLDER_FIRST = "NoDefaultCurrentDirectoryInExePath"
# Git for Windows' bash.exe, by the variable of the folder it is installed under: Pi's own order after shellPath
# (%ProgramFiles%, %ProgramFiles(x86)%), then a per-user install, which Pi finds only through `where`
GIT_BASH = (("ProgramFiles", ("Git", "bin", "bash.exe")),
            ("ProgramFiles(x86)", ("Git", "bin", "bash.exe")),
            ("LOCALAPPDATA", ("Programs", "Git", "bin", "bash.exe")))
# WSL's launchers, which would run Pi's commands inside a WSL distribution: never Pi's shell from here
NEVER_BASH = (("SystemRoot", ("System32", "bash.exe")), ("SystemRoot", ("Sysnative", "bash.exe")),
              ("LOCALAPPDATA", ("Microsoft", "WindowsApps", "bash.exe")))
# What Pi starts by a bare name on Windows, looked up in the folder it is opened in first (C-P1.4a): where (for its
# shells), bash, pwsh and powershell, fd, fdfind and rg (when not placed), git (its footer), taskkill (its MCP
# client), tar (its downloads), npm (its packages), node, gh (/share), clip, rundll32 and cmd (a user's action). A
# folder holding one of them at its top is not opened from here.
PLANTED = ("where", "bash", "pwsh", "powershell", "fd", "fdfind", "rg", "git", "taskkill", "tar", "npm", "node",
           "gh", "clip", "rundll32", "cmd")
ENDINGS = (".COM", ".EXE", ".BAT", ".CMD")  # cross-spawn's which@2.0.2's own, where PATHEXT is not set
# names never handed to Pi from the platform's environment: the hosted providers' keys and settings (the harnesses'
# list), every PI_* (its folders, its OAuth callback's host, its own switches: the plugin sets its own), Node.js's and
# npm's settings (NODE_OPTIONS would run code of its own in Pi); with every pair of Liminal's, which the harness base
# adds (AiPlugin.dropped)
DROP = ("ANTHROPIC_*", "OPENAI_*", "AZURE_*", "OPENROUTER_*", "GEMINI_*", "GOOGLE_API_KEY",
        "GOOGLE_GENERATIVE_AI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS", "GCP_*", "AWS_*", "BEDROCK_*", "MISTRAL_*",
        "GROQ_*", "DEEPSEEK_*", "XAI_*", "COHERE_*", "TOGETHER_*", "FIREWORKS_*", "PERPLEXITY_*", "CEREBRAS_*",
        "NVIDIA_*", "KIMI_*", "MOONSHOT_*", "ZAI_*", "HF_TOKEN", "OLLAMA_*", "LM_STUDIO_*", "HOSTED_VLLM_*",
        "LITELLM_*", "OTEL_*", "OPENCODE_*", "AIDER_*", "CONTINUE_*", "GOOSE_*", "CODEX_*", "COPILOT_*",
        "GITHUB_COPILOT_TOKEN", "PI_*", "NODE_*", "npm_config_*", "NPM_CONFIG_*")
