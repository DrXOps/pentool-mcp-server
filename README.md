# 🧠 pentool-mcp-server

<div align="center">

**MCP-сервер для [Pentool](https://github.com/DrXOps/pentool) — локального AI-ассистента для пентеста**

[![PyPI version](https://img.shields.io/pypi/v/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Open in GitHub](https://img.shields.io/github/stars/DrXOps/pentool-mcp-server?style=social)](https://github.com/DrXOps/pentool-mcp-server)

Самодостаточный **stdio JSON-RPC 2.0** сервер, который даёт AI-функции любому
MCP-клиенту — в первую очередь **Pentool** (BYO-LLM: подбор чеков, обход WAF,
поиск неочевидных эндпоинтов).

</div>

---

## Зачем это отдельный пакет

[MCP](https://modelcontextprotocol.io) — открытый протокол для подключения LLM-моделей
к инструментам. `pentool-mcp-server` инкапсулирует MCP-слое `pentool` как
переиспользуемый PyPI-пакет: **подключается локально (stdio), без сети и без портов**,
устанавливается за секунду, не тащит лишних зависимостей.

## 🔗 Сделано для Pentool

Этот сервер — **MCP-компонент [Pentool](https://github.com/DrXOps/pentool)**, проф.
терминала тестирования веб-безопасности (Burp-совместимый proxy, scanner, spider,
intruder — всё в TUI). Модель генерирует для Pentool:

- 🎯 подбор релевантных **сканирующих чеков** под конкретную цель;
- 🛡 обход WAF / подбор payload;
- 🕷 поиск **неочевидных эндпоинтов** при spider-краулинге.

> Попробуй фуллстек: `pip install "pentool[ai]"` → `pentool ai setup` → `pentool`.

## ⚡ Быстрый старт

```bash
# отдельно (только MCP-сервер)
pip install pentool-mcp-server
pentool-mcp-server --version

# или вместе с Pentool и AI-зависимостями
pip install "pentool[ai]"
```

Проверка живости (stdio):

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | pentool-mcp-server
# → {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
```

## 🚀 Быстрая установка на VPS / в контейнере

Сервер **не открывает портов** и работает как локальный подпроцесс — безопасен
на любом хосте. Запуск через `uv`/`pipx` без загрязнения окружения:

```bash
pipx install pentool-mcp-server    # или: uv tool install pentool-mcp-server
pentool-mcp-server --version
```

Дальше — [`docs/GUIDE.md`](docs/GUIDE.md): полный юзергайд (установка, CLI,
протокол, безопасность).

## 🧩 MCP-инструменты

| Инструмент | Описание |
|-----------|----------|
| `initialize` | Согласование протокола MCP |
| `tools/list` | Список доступных инструментов |
| `tools/call generate` | Сгенерировать ответ LLM по задаче (`task` + `payload`) |
| `tools/call health` | Проверка готовности (установлена ли модель) |
| `tools/call configure` | Указать путь к GGUF-модели |
| `ping` | Проверка живости процесса |

## 🔒 Безопасность

- **Нет сети по умолчанию.** `pentool-mcp-server` слушает только **stdio**
  (stdin → stdout) внутри локального процесса. Внешние обращения к нему
  невозможны — ни с других процессов, ни с другого хоста.
- **Не используйте TCP/0.0.0.0-режим без аутентификации.** Если запускать
  сервер в сетевом режиме наружу, любой, кто сможет писать в stdin/порт,
  получит вызов `tools/call generate` (расход ресурсов + отправка данных цели
  в LLM). Протокол MCP сам по себе **не имеет аутентификации** — держите
  bind на `127.0.0.1`, а доступ контролируйте на уровне межсетевого экрана.
- **Конфиденциальность цели.** Данные (URL, payload) реально покидают host
  только если подключён внешний LLM-провайдер; с локальной GGUF-моделью трафик
  не покидает машину.

Подробнее — [`docs/GUIDE.md`](docs/GUIDE.md#Безопасность).

## 🗺 Дорожная карта

- [x] stdio JSON-RPC 2.0 сервер (initialize / tools/list / tools/call / ping)
- [x] тулы `generate`, `health`, `configure`
- [ ] реальный LLM-раннер (llama-cpp-python) в `model.py`
- [ ] опциональный TCP-режим с HMAC-аутентификацией

## 📄 Лицензия

**AGPL-3.0** — та же лицензия, что и [Pentool](https://github.com/DrXOps/pentool).

---

**Поддержка / баги:** [issues](https://github.com/DrXOps/pentool-mcp-server/issues) · Спроектирован для [Pentool](https://github.com/DrXOps/pentool) · [User Guide](docs/GUIDE.md)
