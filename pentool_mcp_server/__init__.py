"""pentool-mcp-server — MCP-сервер для Pentool AI.

Самодостаточный stdio JSON-RPC 2.0 сервер, устанавливаемый отдельным
PyPI-пакетом `pentool-mcp-server` и запускаемый командой
`pentool-mcp-server`. Используется pentool как MCP-бэкенд (см.
pentool/services/ai/provider.MCPBackend).
"""

from pentool_mcp_server.__main__ import __version__, main, run_stdio_server

__all__ = ["__version__", "main", "run_stdio_server"]
