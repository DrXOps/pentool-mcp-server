# pentool-mcp-server

MCP-сервер для **Pentool AI** — самодостаточный JSON-RPC 2.0 (stdio) сервер,
устанавливаемый как отдельный PyPI-пакет и используемый pentool в качестве
MCP-бэкенда.

**Репозиторий**: отдельный (этот пакет вынесен из основной кодовой базы pentool).

## Установка

```bash
pip install pentool-mcp-server
# или в составе pentool с AI-зависимостями:
pip install "pentool[ai]"
```

## Запуск

```bash
pentool-mcp-server            # stdio-режим (JSON-RPC построчно)
pentool-mcp-server --version  # версия
```

## MCP-инструменты

| Инструмент | Описание |
|-----------|----------|
| `initialize` | Согласование протокола |
| `tools/list` | Список инструментов |
| `tools/call generate` | Сгенерировать ответ LLM по задаче (task + payload) |
| `tools/call health` | Проверка готовности (установлена ли модель) |
| `tools/call configure` | Указать путь к GGUF-модели |
| `ping` | Проверка живости |

## Пример (stdio)

```bash
$ echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | pentool-mcp-server
{"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
```

## Интеграция с pentool

- `pentool ai setup` доустанавливает этот пакет (extra `[ai]`).
- `pentool.services.ai.factory._build_mcp_cmd` предпочитает запускать
  `pentool-mcp-server` (через `shutil.which`), а не inline-скрипт-заглушку.

## Разработка

Пакет живёт в `ai_server/` внутри основного репозитория pentool для
варианта подготовки; при публикации каталог `ai_server/` переносится в
отдельный GitHub-репозиторий `DrXOps/pentool-mcp-server` и собирается в
собственный wheel на PyPI. `model.py` — точка расширения для реального
LLM-раннера (llama-cpp-python и т.п.).
