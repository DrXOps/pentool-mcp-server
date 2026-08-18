"""Загрузка и генерация LLM для pentool-mcp-server.

Этот модуль импортируется лениво (только при tools/call generate) — чтобы
логика загрузки GGUF-модели не тянула тяжёлые зависимости (llama-cpp) при
простых health/ping. Попытка загрузить модель выполняется через выбранную
библиотеку; при отсутствии прав/зависимостей возвращает пустой результат,
не падая.

Точка расширения: здесь позже подключается реальный llama-cpp-python (или
любой другой раннер), а внешний интерфейс generate() остаётся стабильным.
"""

from __future__ import annotations

import json
from typing import Any


async def generate(task: str, payload: str, model: str | None) -> dict[str, Any] | None:
    """Сгенерировать ответ LLM для задачи.

    Args:
        task: имя задачи (choose_checks / crawl_endpoints / ...).
        payload: JSON-строка с данными цели/контекстом.
        model: путь к GGUF-файлу модели (или None).

    Returns:
        dict с результатом (например {"items": [...]}) или None, если
        модель недоступна / генерация не реализована для этой задачи.
    """
    if not model:
        return None

    try:
        ctx = json.loads(payload) if payload else {}
    except Exception:  # noqa: BLE001
        ctx = {}

    # Плейсхолдер: здесь должна вызываться реальная LLM-модель.
    # Пока возвращаем структуру "модель установлена, LLM не подключён",
    # чтобы health/MCP-протокол работали честно до интеграции раннера.
    return {
        "task": task,
        "model": model,
        "status": "model-ok-not-connected",
        "items": [],
    }
