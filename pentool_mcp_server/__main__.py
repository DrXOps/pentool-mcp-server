"""pentool-mcp-server — самодостаточный JSON-RPC (stdio) сервер для Pentool AI.

Обращается по однострочному JSON-RPC 2.0 через stdin/stdout (стандартный
MCP-протокол). Предоставляет инструменты:
  - initialize     — согласование протокола
  - tools/list     — список доступных инструментов
  - tools/call     — вызов инструмента (generate / health / configure)
  - ping           — проверка живости

Устанавливается как PyPI-пакет (`pentool-mcp-server`) и запускается командой
`pentool-mcp-server`. Вся работа с LLM-моделью вынесена в отдельный модуль
`model.py`, который загружается лениво (не тянет тяжёлые зависимости при
простом ping / health).
"""

from __future__ import annotations

import json
import sys
from typing import Any

__version__ = "0.1.0"
__all__ = ["run_stdio_server", "main"]


# ── Схемы инструментов ──────────────────────────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "generate",
        "description": "Сгенерировать ответ LLM по задаче. payload — строка "
                       "запроса (данные цели), model — путь к GGUF-файлу "
                       "модели (необязательно). При отсутствии модели вернёт "
                       "ошибку setup required.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Имя задачи (напр. choose_checks, crawl_endpoints)"},
                "payload": {"type": "string", "description": "Данные цели / контекст (JSON-строка)"},
                "model": {"type": "string", "description": "Путь к GGUF-файлу модели"},
            },
            "required": ["task", "payload"],
        },
    },
    {
        "name": "health",
        "description": "Проверка готовности: вернёт статус, установлена ли модель.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "configure",
        "description": "Принять параметры конфигурации сервера (напр. путь модели).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Путь к GGUF-файлу модели"},
            },
        },
    },
]

# Состояние сервера (глобальное на процесс).
_STATE: dict[str, Any] = {"model": None}


def _default_model_path() -> str | None:
    """Найти GGUF-модель в ~/.pentool/ai/models/. Лёгкая проверка FS."""
    from pathlib import Path
    models_dir = Path.home() / ".pentool" / "ai" / "models"
    if not models_dir.exists():
        return None
    for f in sorted(models_dir.iterdir()):
        if f.suffix in (".gguf", ".bin"):
            return str(f)
    return None


# ── Обработчики ─────────────────────────────────────────────────────────────

def _handle_initialize(req: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req.get("id", 1),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "pentool-mcp-server", "version": __version__},
        },
    }


def _handle_tools_list(req: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req.get("id", 1),
        "result": {"tools": TOOLS},
    }


def _handle_ping(req: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req.get("id", 1),
        "result": {"status": "ok"},
    }


async def _run_generate(task: str, payload: str, model: str | None) -> dict | None:
    """Вызвать LLM-модель для задачи. Ленивый импорт model.py.

    Возвращает dict ответа или None, если модель недоступна.
    """
    from pentool_mcp_server import model
    return await model.generate(task, payload, model or _STATE.get("model"))


def _handle_tools_call(req: dict) -> dict:
    params = req.get("params", {})
    name = params.get("name", "")
    args = params.get("arguments", {}) or {}

    if name == "health":
        model_path = _STATE.get("model") or _default_model_path()
        ready = bool(model_path)
        return {
            "jsonrpc": "2.0",
            "id": req.get("id", 1),
            "result": {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "ok": ready,
                        "model_present": ready,
                        "model": model_path or None,
                        "setup_required": not ready,
                    }, ensure_ascii=False),
                }],
            },
        }

    if name == "configure":
        new_model = args.get("model")
        if new_model:
            _STATE["model"] = new_model
        return {
            "jsonrpc": "2.0",
            "id": req.get("id", 1),
            "result": {"content": [{"type": "text", "text": "configured"}]},
        }

    if name == "generate":
        task = args.get("task", "")
        payload = args.get("payload", "")
        model = args.get("model") or _STATE.get("model") or _default_model_path()
        if not model:
            return {
                "jsonrpc": "2.0",
                "id": req.get("id", 1),
                "error": {
                    "code": -32000,
                    "message": "Model not installed. Run: pentool ai setup",
                },
            }
        try:
            loop = sys.modules.get("asyncio")
            import asyncio
            if asyncio.get_event_loop().is_running():
                # Уже в asyncio-контексте — это не должно случиться в stdio-цикле
                result = _run_generate(task, payload, model)
            else:
                result = asyncio.run(_run_generate(task, payload, model))
        except Exception as exc:  # noqa: BLE001
            return {
                "jsonrpc": "2.0",
                "id": req.get("id", 1),
                "error": {"code": -32000, "message": f"generate failed: {exc}"},
            }
        return {
            "jsonrpc": "2.0",
            "id": req.get("id", 1),
            "result": {"content": [{"type": "text", "text": json.dumps(result or {})}],
                       "is_error": result is None},
        }

    return {
        "jsonrpc": "2.0",
        "id": req.get("id", 1),
        "error": {"code": -32601, "message": f"Tool not found: {name}"},
    }


dispatch_table = {
    "initialize": _handle_initialize,
    "tools/list": _handle_tools_list,
    "tools/call": _handle_tools_call,
    "ping": _handle_ping,
}


def _handle_request(req: dict) -> dict:
    method = req.get("method", "")
    handler = dispatch_table.get(method)
    if handler is None:
        return {
            "jsonrpc": "2.0",
            "id": req.get("id", 1),
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
    try:
        return handler(req)
    except Exception as exc:  # noqa: BLE001
        return {
            "jsonrpc": "2.0",
            "id": req.get("id", 1),
            "error": {"code": -32603, "message": f"Internal error: {exc}"},
        }


# ── Цикл stdio ──────────────────────────────────────────────────────────────


async def _amain() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle_request(req)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def run_stdio_server() -> None:
    """Запустить сервер в синхронном stdio-цикле (без участия LLM)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle_request(req)
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def main() -> int:
    """Консольный entry point: `pentool-mcp-server`."""
    args = sys.argv[1:]
    if "--version" in args or "-V" in args:
        print(f"pentool-mcp-server {__version__}")
        return 0
    try:
        run_stdio_server()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
