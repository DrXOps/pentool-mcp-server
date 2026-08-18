> [**English (EN)**](../../README.md) · **Русский (RU)**

# 🧠 pentool-mcp-server

<div align="center">

**MCP-сервер для [Pentool](https://github.com/DrXOps/pentool) — локального AI-ассистента для веб-пентеста**

[![PyPI version](https://img.shields.io/pypi/v/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/pentool-mcp-server.svg)](https://pypi.org/project/pentool-mcp-server/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Install: uv](https://img.shields.io/badge/Install-uv-4051B5.svg)](https://docs.astral.sh/uv/)
[![Open in GitHub](https://img.shields.io/github/stars/DrXOps/pentool-mcp-server?style=social)](https://github.com/DrXOps/pentool-mcp-server)

Самодостаточный **stdio JSON-RPC 2.0** сервер, который даёт AI-функции любому
MCP-клиенту — в первую очередь **Pentool** (BYO-LLM: подбор чеков, обход WAF,
поиск неочевидных эндпоинтов). Устанавливается через **uv** одной командой.

</div>

---

## Зачем это отдельный пакет

[MCP](https://modelcontextprotocol.io) — открытый протокол для подключения LLM-моделей
к инструментам. `pentool-mcp-server` инкапсулирует MCP-слой `pentool` как
переиспользуемый PyPI-пакет: **подключается локально (stdio), без сети и без портов**,
устанавливается за секунды, без лишних зависимостей.

## 🔗 Сделано для Pentool

Этот сервер — **MCP-компонент [Pentool](https://github.com/DrXOps/pentool)**,
профессионального терминала тестирования веб-безопасности (proxy-совместимый с Burp,
scanner, spider, intruder — всё в TUI). Он даёт Pentool AI:

- 🎯 подбор релевантных **скан-чеков** под конкретную цель;
- 🛡 обход WAF / подбор payload;
- 🕷 поиск **неочевидных эндпоинтов** при spider-краулинге.

> Полный стек: `uv tool install "pentool[ai]"` → `pentool ai setup` → `pentool`.

## ⚡ Быстрый старт (uv)

```bash
# Установить uv (если ещё нет): https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Только MCP-сервер
uv tool install pentool-mcp-server
pentool-mcp-server --version

# Или вместе с Pentool и AI-зависимостями
uv tool install "pentool[ai]"
```

Проверка живости (stdio):

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"ping"}' | pentool-mcp-server
# → {"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}
```

> **uv — стандартный способ установки** — изолированное окружение, ровно как
> устанавливается сам Pentool. Сервер при этом не трогает системный Python.

## 🚀 Развёртывание на VPS / в контейнере

Сервер **не открывает портов** и работает как локальный подпроцесс — безопасен
на любом хосте. Через uv он живёт вне системного Python:

```bash
uv tool install pentool-mcp-server
```

Полный гайд — [`docs/GUIDE.md`](../../docs/GUIDE.md). Английская версия README — [EN](../../README.md).

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
  (stdin → stdout) внутри локального процесса. Внешние обращения невозможны —
  ни с других процессов, ни с другого хоста.
- **Не запускайте в TCP/0.0.0.0-режиме без аутентификации.** Если выставить
  сервер в сеть наружу, любой, кто сможет писать в stdin/порт, получит
  `tools/call generate` (расход ресурсов + отправка данных цели в LLM). MCP
  **не имеет встроенной аутентификации** — держите bind на `127.0.0.1` и
  закрывайте снаружи межсетевым экраном.
- **Конфиденциальность цели.** Данные (URL, payload) покидают host только при
  подключении внешнего LLM-провайдера; с локальной GGUF-моделью трафик остаётся
  на машине.

Подробнее — [`docs/GUIDE.md`](../../docs/GUIDE.md#Безопасность).

## 🗺 Дорожная карта

- [x] stdio JSON-RPC 2.0 сервер (initialize / tools/list / tools/call / ping)
- [x] тулы `generate`, `health`, `configure`
- [ ] реальный LLM-раннер (llama-cpp-python) в `model.py`
- [ ] опциональный TCP-режим с HMAC-аутентификацией

## 📄 Лицензия

**AGPL-3.0** — та же лицензия, что и [Pentool](https://github.com/DrXOps/pentool).

---

**Поддержка / баги:** [issues](https://github.com/DrXOps/pentool-mcp-server/issues) · Сделан для [Pentool](https://github.com/DrXOps/pentool) · [User Guide](../../docs/GUIDE.md)
