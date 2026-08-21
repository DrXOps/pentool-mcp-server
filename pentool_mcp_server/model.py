"""Загрузка и генерация LLM для pentool-mcp-server.

Этот модуль импортируется лениво (только при tools/call generate) — чтобы
логика загрузки GGUF-модели не тянула тяжёлые зависимости (llama-cpp-python)
при простых health/ping.

Реализация использует llama-cpp-python. ЕСЛИ пакет не установлен — generate()
возвращает детальную ошибку "llama-cpp-python not installed" вместо молчаливого
пустого ответа, чтобы пользователь видел причину, а не «AI не ответил».

Формат ответа совместим с клиентом (pentool/services/ai/provider.py): клиент
ожидает dict, у которого может быть массив под ключом "items" (или сам dict,
или список). Для задач, чья expected_json_schema имеет тип array, раннер
возвращает {"items": [ ... ]}.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

__all__ = ["generate", "is_llama_available"]

# Загруженная модель кэшируется на процесс (час-лоада GGUF ~секунды-десятки
# секунд; не будем грузить на каждый вызов). Ключ — путь к файлу.
_LOADED: dict[str, Any] = {}


def is_llama_available() -> bool:
    """True, если llama-cpp-python установлен и импортируется."""
    try:
        import llama_cpp  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


def _get_llm(model_path: str):
    """Получить (и кешировать) загруженный Llama для переданного GGUF-файла.

    model_path приводится к строке принудительно (os.fspath), чтобы изолировать
    любые шадоу-конфликты имён (например, если через runpy в процесс попало
    глобальное имя, ссылающееся на модуль) и избежать llama-cpp ошибки
    «stat: path ... not module».
    """
    import os
    path = os.fspath(model_path)
    if path in _LOADED:
        return _LOADED[path]
    from llama_cpp import Llama
    # LFM2.5-350M — лёгкая edge-модель; 8K контекста хватает для задач
    # payload/endpoint и помещается в RAM даже на слабой машине.
    llm = Llama(model_path=path, n_ctx=8192, verbose=False)
    _LOADED[path] = llm
    return llm


def _chatml(messages: list[dict[str, str]]) -> str:
    """Собрать строку в ChatML-формате (LFM2.5-heretic использует ChatML)."""
    parts: list[str] = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "system":
            parts.append(f"<|im_start|>system\n{content}<|im_end|>\n")
        elif role == "user":
            parts.append(f"<|im_start|>user\n{content}<|im_end|>\n")
        elif role == "assistant":
            parts.append(f"<|im_start|>assistant\n{content}<|im_end|>\n")
    parts.append("<|im_start|>assistant\n")
    return "".join(parts)


def _extract_json(text: str) -> Any:
    """Извлечь JSON из ответа LLM, устойчиво к обвязке (code fences, лишний текст).

    Пытается: 1) целиком, 2) блок внутри ```json ... ```, 3) первое вхождение
    '{'... '}' или '[' ... ']' на верхнем уровне. Иначе возвращает None.
    """
    text = text.strip()
    # 1) Полный ответ уже JSON.
    try:
        return json.loads(text)
    except Exception:  # noqa: BLE001
        pass
    # 2) Блок ```json ... ``` / ```json\n...
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:  # noqa: BLE001
            pass
    # 3) Дальше — ищем массив или объект от первого [ или { до сбалансированной
    #    закрывающей скобки.
    for opener, closer in (("[", "]"), ("{", "}")):
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == opener:
                depth += 1
            elif text[i] == closer:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except Exception:  # noqa: BLE001
                        break
    return None


async def generate(
    task: str,
    system_prompt: str | None,
    context: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
    model: str | None,
) -> dict[str, Any] | None:
    """Сгенерировать ответ LLM для задачи.

    Args:
        task: имя задачи (choose_checks / crawl_endpoints / ...).
        system_prompt: системный промпт задачи (передаётся клиентом).
        context: данные цели/контекст (JSON).
        max_tokens: макс. токенов ответа.
        temperature: температура генерации.
        model: путь к GGUF-файлу модели (или None).

    Returns:
        dict с результатом, нормализованный для клиента. Для массив-задач это
        {"items": [...]}. None только при недоступности модели/промпта.
    """
    if not model:
        return None
    if not is_llama_available():
        return {
            "error": (
                "llama-cpp-python is not installed in the MCP server environment. "
                "Run: uv tool install pentool-mcp-server --with llama-cpp-python"
            ),
        }
    if not system_prompt:
        return {"error": "No system_prompt for task"}

    user_content = json.dumps(context, ensure_ascii=False) if context is not None else ""
    prompt_text = _chatml([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ])

    try:
        llm = await asyncio.to_thread(_get_llm, model)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Failed to load model: {exc}"}

    # Bound-метод create_chat_completion уже привязан к llm — его НЕ нужно
    # передавать первым аргументом (это была ошибка «has no element 0»).
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    try:
        if hasattr(llm, "create_chat_completion"):
            output = await asyncio.to_thread(
                llm.create_chat_completion,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|im_end|>"],
            )
        else:
            output = await asyncio.to_thread(_legacy_completion, llm, prompt_text, max_tokens, temperature)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Inference failed: {exc}"}

    raw = _response_text(output) or ""
    parsed = _extract_json(raw)

    # Если задача ожидает массив, нормализуем к {"items": [...]}.
    if isinstance(parsed, list):
        return {"items": parsed}
    if isinstance(parsed, dict):
        return parsed
    # Не JSON — вернём raw текст, чтобы клиент не потерял ответ молча.
    return {"items": [], "raw": raw}


def _legacy_completion(llm, prompt_text: str, max_tokens: int, temperature: float) -> Any:
    """Fallback для версий llama-cpp-python без create_chat_completion."""
    return llm(
        prompt_text,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["<|im_end|>"],
    )


def _response_text(output: Any) -> str | None:
    """Вытащить text из ответа llama-cpp-python (разные версии — разный формат)."""
    if not output:
        return None
    try:
        # Chat-style: choices[0].message.content
        return output["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001
        try:
            # Completion-style: choices[0].text
            return output["choices"][0]["text"]
        except Exception:  # noqa: BLE001
            return None
