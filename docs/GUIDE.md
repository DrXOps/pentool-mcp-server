# User Guide — pentool-mcp-server

Минимальное руководство по установке, запуску и использованию MCP-сервера для
[Pentool](https://github.com/DrXOps/pentool).

## Что это

`pentool-mcp-server` — stdio JSON-RPC 2.0 сервер. Общается построчно через
stdin → stdout, без сети и без портов. Используется Pentool как MCP-бэкенд для
локального AI.

## Установка

Установка через **uv** (рекомендуется) — изолированное окружение, как у самого
Pentool.

### Однострочник

```bash
uv tool install pentool-mcp-server
```

### Вместе с Pentool (AI-extra)

```bash
uv tool install "pentool[ai]"         # MCP-сервер + AI-extra
```

### Из исходников (это репо)

```bash
git clone https://github.com/DrXOps/pentool-mcp-server.git
cd pentool-mcp-server
uv tool install .                     # или: uvx --from . pentool-mcp-server
```

## Запуск

```bash
pentool-mcp-server            # stdio-режим (построчный JSON-RPC)
pentool-mcp-server --version  # печать версии
```

## Проверка (smoke)

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | pentool-mcp-server
# {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
```

## MCP-протокол (примеры)

### tools/list

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | pentool-mcp-server
```

### tools/call health

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"health","arguments":{}}}' \
  | pentool-mcp-server
```

### tools/call generate

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"generate","arguments":{"task":"choose_checks","payload":"{\"url\":\"https://example.com\"}"}}}' \
  | pentool-mcp-server
```

`generate` возвращает ошибку `setup required` (`-32000`), если не установлена
GGUF-модель. Модель подключается через `tools/call configure` с аргументом
`{"model":"/path/to/model.gguf"}` либо по пути по умолчанию
`~/.pentool/ai/models/`.

## Интеграция с Pentool

- `pentool ai setup` доустанавливает этот пакет (extra `[ai]`).
- `pentool.services.ai.factory._build_mcp_cmd` предпочитает запускать
  `pentool-mcp-server` (через `shutil.which`), а не inline-скрипт-заглушку.
- На дашборде Pentool статус MCP отражается в LED: `RUNNING` / `READY` / `OFF`.

## Безопасность

- По умолчанию сервер **не открывает порты** — работает только через stdio
  локального процесса. Внешний доступ невозможен.
- **Не запускайте в TCP/0.0.0.0-режиме без аутентификации**: MCP-протокол не
  имеет встроенной auth; злоумышленник, получивший доступ к stdin/порту, смог
  бы вызывать `generate` (расход ресурсов, утечка данных цели в LLM). Держите
  bind на `127.0.0.1` и закрывайте наружу межсетевым экраном.
- С локальной GGUF-моделью данные цели не покидают машину.

## Разработка

- `model.py` — точка расширения для реального LLM-раннера (llama-cpp-python и
  т.п.). Сейчас возвращает структуру `{"status":"model-ok-not-connected"}`.
- Билд, smoke и публикация на PyPI — через `.github/workflows/publish.yml`
  (trusted publishing на пуш тега `v*`).

## Репозитории

- Этот сервер: https://github.com/DrXOps/pentool-mcp-server
- Приложение, для которого он создан: https://github.com/DrXOps/pentool
