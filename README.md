> **English** · [**Русский (RU)**](docs/i18n/ru/README.md)

# 🧠 pentool-mcp-server

<div align="center">

**MCP server for [Pentool](https://github.com/DrXOps/pentool) — the local AI assistant for web pentesting**

[![PyPI version](https://img.shields.io/pypi/v/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Install: uv](https://img.shields.io/badge/Install-uv-4051B5.svg)](https://docs.astral.sh/uv/)
[![Open in GitHub](https://img.shields.io/github/stars/DrXOps/pentool-mcp-server?style=social)](https://github.com/DrXOps/pentool-mcp-server)

A self-contained **stdio JSON-RPC 2.0** server that brings AI capabilities to any
MCP client — first of all to **Pentool** (BYO-LLM: picking checks, bypassing WAF,
finding non-obvious endpoints). Installed with **uv** in one command.

</div>

---

## Why a separate package

[MCP](https://modelcontextprotocol.io) is the open protocol for connecting LLM
models to tools. `pentool-mcp-server` encapsulates Pentool's MCP layer as a
reusable PyPI package: **attached locally (stdio), no network, no ports**, installs
in seconds, no heavy dependencies.

## 🔗 Built for Pentool

This server is the **MCP component of [Pentool](https://github.com/DrXOps/pentool)**,
a professional web-security testing terminal (Burp-compatible proxy, scanner,
spider, intruder — all in a TUI). It powers Pentool's AI:

- 🎯 picking the relevant **scan checks** for a concrete target;
- 🛡 WAF bypass / payload suggestions;
- 🕷 finding **non-obvious endpoints** during spider crawling.

> Try the full stack: `uv tool install "pentool[ai]"` → `pentool ai setup` → `pentool`.

## ⚡ Quick start (uv)

```bash
# Install uv (if not present): https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Standalone — just the MCP server
uv tool install pentool-mcp-server
pentool-mcp-server --version

# Or together with Pentool and its AI extras
uv tool install "pentool[ai]"
```

Health check (stdio):

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | pentool-mcp-server
# → {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
```

> **uv** is the standard install path — isolated environment, exactly how
> Pentool itself is installed. It keeps the server out of your system Python.

## 🚀 Deploy on a VPS / in a container

The server **opens no ports** and runs as a local subprocess — safe on any host.
With uv it stays out of the system Python:

```bash
uv tool install pentool-mcp-server
```

Full user guide — [`docs/GUIDE.md`](docs/GUIDE.md). Russian — [README.ru](docs/i18n/ru/README.md).

## 🧩 MCP tools

| Tool | Description |
|------|-------------|
| `initialize` | MCP protocol handshake |
| `tools/list` | List available tools |
| `tools/call generate` | Generate an LLM answer for a task (`task` + `payload`) |
| `tools/call health` | Readiness check (is a model installed) |
| `tools/call configure` | Point to a GGUF model path |
| `ping` | Process liveness |

## 🔒 Security

- **No network by default.** `pentool-mcp-server` listens only on **stdio**
  (stdin → stdout) inside the local process. External access is impossible —
  neither from other processes nor from another host.
- **Do not expose it over TCP/0.0.0.0 without auth.** If run on a network port
  outwardly, anyone able to write to stdin/port gets `tools/call generate`
  (resource usage + sending target data to the LLM). MCP has **no built-in
  authentication** — bind to `127.0.0.1` and gate via a firewall.
- **Target privacy.** Data (URL, payload) leaves the host only if an external LLM
  provider is connected; with a local GGUF model the traffic stays on the machine.

More — [`docs/GUIDE.md`](docs/GUIDE.md#Security).

## 🗺 Roadmap

- [x] stdio JSON-RPC 2.0 server (initialize / tools/list / tools/call / ping)
- [x] `generate`, `health`, `configure` tools
- [ ] real LLM runner (llama-cpp-python) in `model.py`
- [ ] optional TCP mode with HMAC auth

## 📄 License

**AGPL-3.0** — the same license as [Pentool](https://github.com/DrXOps/pentool).

---

**Support / bugs:** [issues](https://github.com/DrXOps/pentool-mcp-server/issues) · Designed for [Pentool](https://github.com/DrXOps/pentool) · [User Guide](docs/GUIDE.md)
