"""Optional chat-completions assistant with a safe local demo fallback."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

AI_TIMEOUT_SECONDS = 12
MAX_PROVIDER_ATTEMPTS = 3
RETRY_INITIAL_DELAY_SECONDS = 0.25
MAX_LOGGED_PROVIDER_ERROR_CHARS = 160
PROVIDER_ATTEMPT_TIMEOUT_SECONDS = AI_TIMEOUT_SECONDS / MAX_PROVIDER_ATTEMPTS
logger = logging.getLogger(__name__)
DEFAULT_PROVIDER_URL = "https://api.groq.com/openai/v1/chat/completions"

def provider_key_present() -> bool:
    return bool(os.getenv("SAPNA_AI_API_KEY", "").strip())

def log_provider_key_status(stage: str) -> None:
    logger.info("AI provider configuration at %s: pid=%s SAPNA_AI_API_KEY present=%s", stage, os.getpid(), provider_key_present())

# These are invented examples for conversation practice, not verified schemes.
DEMO_KNOWLEDGE = [
    {"name": "Post-Matric Scholarship (mock)", "topic": "illustrative post-school study support", "status": "fictional demo example; no verified rules or dates"},
    {"name": "Rural Talent Scholarship (mock)", "topic": "illustrative rural student support", "status": "fictional demo example; no verified rules or dates"},
    {"name": "Kanya Shiksha Protsahan (mock)", "topic": "illustrative girls education support", "status": "fictional demo example; no verified rules or dates"},
    {"name": "Learning Pathway Award (mock)", "topic": "illustrative help continuing education", "status": "fictional demo example; no verified rules or dates"},
    {"name": "Community Study Support (mock)", "topic": "illustrative community study support", "status": "fictional demo example; no verified rules or dates"},
]

DOCUMENT_GUIDANCE: dict[str, dict[str, str]] = {
    "aadhaar": {"why": "Some providers may ask for identity proof to match an application. This demo never needs an identity number.", "next": "Check the selected provider's current notice for accepted identity proofs. Ask a trusted adult or school office if you need help."},
    "marksheet": {"why": "A provider may ask for marksheets to confirm study history or an academic criterion.", "next": "Ask your school office for a copy or for help obtaining a replacement."},
    "income": {"why": "Some providers use an income certificate for their own income criteria.", "next": "First confirm the document is required in the official notice. Then ask your local issuing authority or authorized service centre about its current process."},
    "bank": {"why": "A provider may request account details to pay an approved benefit.", "next": "Check if the scheme requires a student account. Ask a bank and trusted adult about current steps; never enter account numbers in this demo."},
    "photo": {"why": "An application form may request a recent photo for identification.", "next": "Check the current form's photo, file-size, and format requirements before preparing one."},
    "caste": {"why": "Some providers may request a category certificate for their own criteria.", "next": "Confirm the document is needed, then ask the school or issuing authority about current local steps."},
}

SYSTEM_PROMPT = """You are Sapna Saathi, a friendly scholarship application copilot for rural students. Use short sentences and simple, encouraging language. Explain common application steps and document preparation. Treat the supplied knowledge base as invented demo examples only; never imply government verification, live deadlines, confirmed benefits, official integration, or real scheme requirements. If asked for current facts, say you do not have verified live information and direct the student to the provider's official notice. Never decide, infer, approve, or override eligibility: eligibility is calculated separately by deterministic application rules. You may explain a supplied rule result only as a demo estimate. Never ask for or repeat Aadhaar numbers, bank details, passwords, API keys, or other identity secrets. Do not request unnecessary personal details."""

def _fallback(question: str, document_id: str | None = None) -> str:
    q = question.casefold()
    if document_id in DOCUMENT_GUIDANCE:
        info = DOCUMENT_GUIDANCE[document_id]
        return f"Demo guidance only. {info['why']} Next step: {info['next']}"
    if any(word in q for word in ("deadline", "date", "last date", "when")):
        return "I don't have verified live deadline information. Check the scholarship provider's current official notice. This assistant's scheme examples are mock data."
    if any(word in q for word in ("eligible", "eligibility", "qualify", "match")):
        return "I can't decide eligibility in chat. The app uses separate deterministic demo rules to show possible matches; those are not official decisions. Please verify current criteria with the provider."
    if any(word in q for word in ("document", "certificate", "marksheet", "paper")):
        return "Requirements vary by provider. Check its current official notice, then ask your school or local authorized service centre for help with the listed items. Any scholarship examples in this app are mock data."
    if any(word in q for word in ("apply", "application", "submit", "form")):
        return "Start by checking the provider's current official notice for eligibility, dates, requested documents, and application channel. A school office or trusted adult can help you understand the steps."
    return "I can help you plan application steps and understand common documents. The five scheme examples in this demo are fictional and have no verified requirements, benefits, or deadlines. Check the provider's official notice for current information."

def _sanitize_provider_error(exc: HTTPError, api_key: str, messages: list[dict[str, str]]) -> tuple[str, str]:
    """Extract a short provider error while scrubbing secrets and submitted text."""
    try:
        raw_body = exc.read(4096).decode("utf-8", errors="replace")
        parsed = json.loads(raw_body)
        error = parsed.get("error", {}) if isinstance(parsed, dict) else {}
        message = error.get("message", "") if isinstance(error, dict) else ""
        provider_code = error.get("code", error.get("status", exc.code)) if isinstance(error, dict) else exc.code
        if not isinstance(message, str):
            message = ""
    except (OSError, json.JSONDecodeError):
        message = ""
        provider_code = exc.code

    # Provider errors can echo request text. Remove submitted content wholesale
    # before logging and redact common personal-data/credential formats too.
    submitted_text = sorted(
        (item.get("content", "") for item in messages if isinstance(item.get("content"), str)),
        key=len,
        reverse=True,
    )
    for value in submitted_text:
        if value:
            message = message.replace(value, "[redacted]")
    if api_key:
        message = message.replace(api_key, "[redacted]")
    message = re.sub(r"(?i)bearer\s+\S+", "Bearer [redacted]", message)
    message = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[redacted-email]", message, flags=re.IGNORECASE)
    message = re.sub(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)", "[redacted-number]", message)
    message = re.sub(r"(?i)\b(?:api[_ -]?key|token|secret)\s*[:=]\s*\S+", "credential=[redacted]", message)
    message = " ".join("".join(ch if ch.isprintable() else " " for ch in message).split())
    code = str(provider_code) if isinstance(provider_code, (int, str)) else str(exc.code)
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", code):
        code = str(exc.code)
    safe_message = message[:MAX_LOGGED_PROVIDER_ERROR_CHARS] or "provider returned an error without a safe message"
    return code, safe_message

def _call_provider(messages: list[dict[str, str]]) -> str:
    api_key = os.getenv("SAPNA_AI_API_KEY", "").strip()
    base_url = os.getenv("SAPNA_AI_BASE_URL", DEFAULT_PROVIDER_URL).strip()
    model = os.getenv("SAPNA_AI_MODEL", "").strip()
    if not api_key:
        raise RuntimeError("SAPNA_AI_API_KEY is not configured")
    if not model:
        logger.warning("AI provider failure category=configuration")
        raise RuntimeError("SAPNA_AI_MODEL is not configured")
    parsed_url = urlparse(base_url)
    local_http_hosts = {"localhost", "127.0.0.1", "::1"}
    if not parsed_url.netloc or not (parsed_url.scheme == "https" or (parsed_url.scheme == "http" and parsed_url.hostname in local_http_hosts)):
        logger.warning("AI provider failure category=configuration")
        raise RuntimeError("SAPNA_AI_BASE_URL must use HTTPS (HTTP is allowed for localhost)")
    request_body: dict[str, Any] = {"model": model, "messages": messages}
    if parsed_url.hostname != "generativelanguage.googleapis.com":
        request_body.update({"temperature": 0.3, "max_tokens": 350})
    body = json.dumps(request_body).encode("utf-8")
    request = Request(base_url, data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    for attempt in range(1, MAX_PROVIDER_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=PROVIDER_ATTEMPT_TIMEOUT_SECONDS) as response:
                payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
            text = payload["choices"][0]["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                logger.warning("AI provider failure category=invalid_response")
                raise RuntimeError("The AI provider returned an empty response")
            return text.strip()
        except HTTPError as exc:
            provider_code, safe_message = _sanitize_provider_error(exc, api_key, messages)
            logger.warning("AI provider error code=%s message=%r", provider_code, safe_message)
            if exc.code in {429, 503} and attempt < MAX_PROVIDER_ATTEMPTS:
                time.sleep(RETRY_INITIAL_DELAY_SECONDS * (2 ** (attempt - 1)))
                continue
            raise RuntimeError("The AI provider could not return a response") from None
        except (TimeoutError, asyncio.TimeoutError):
            logger.warning("AI provider failure category=timeout attempt=%s", attempt)
            if attempt < MAX_PROVIDER_ATTEMPTS:
                time.sleep(RETRY_INITIAL_DELAY_SECONDS * (2 ** (attempt - 1)))
                continue
            raise RuntimeError("The AI provider request timed out") from None
        except URLError:
            logger.warning("AI provider failure category=network attempt=%s", attempt)
            if attempt < MAX_PROVIDER_ATTEMPTS:
                time.sleep(RETRY_INITIAL_DELAY_SECONDS * (2 ** (attempt - 1)))
                continue
            raise RuntimeError("The AI provider could not return a response") from None
        except (OSError, KeyError, IndexError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            if isinstance(exc, OSError) and attempt < MAX_PROVIDER_ATTEMPTS:
                logger.warning("AI provider failure category=network attempt=%s", attempt)
                time.sleep(RETRY_INITIAL_DELAY_SECONDS * (2 ** (attempt - 1)))
                continue
            category = "network" if isinstance(exc, OSError) else "invalid_response"
            logger.warning("AI provider failure category=%s attempt=%s", category, attempt)
            raise RuntimeError("The AI provider could not return a response") from None

async def respond(question: str, *, history: list[dict[str, str]], context: dict[str, Any], document_id: str | None = None) -> dict[str, str]:
    key_present = provider_key_present()
    log_provider_key_status("assistant request")
    if not key_present:
        return {"answer": _fallback(question, document_id), "mode": "demo_fallback", "label": "Demo guidance - AI provider not configured"}
    allowed_context = {key: context[key] for key in ("class_level", "course", "rural", "completed_documents") if key in context}
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\nDemo knowledge base: " + json.dumps(DEMO_KNOWLEDGE) + "\nLimited student context: " + json.dumps(allowed_context)},
        *history[-8:],
        {"role": "user", "content": question},
    ]
    try:
        answer = await asyncio.wait_for(asyncio.to_thread(_call_provider, messages), timeout=AI_TIMEOUT_SECONDS + 1)
        return {"answer": answer, "mode": "llm", "label": "AI-assisted response - verify current details with the provider"}
    except asyncio.TimeoutError:
        logger.warning("AI provider failure category=timeout")
        return {"answer": _fallback(question, document_id), "mode": "demo_fallback", "label": "Demo guidance - AI provider unavailable"}
    except RuntimeError:
        return {"answer": _fallback(question, document_id), "mode": "demo_fallback", "label": "Demo guidance - AI provider unavailable"}

async def chat(question: str, history: list[dict[str, str]], context: dict[str, Any]) -> dict[str, str]:
    return await respond(question, history=history, context=context)

async def guidance(document_id: str, context: dict[str, Any]) -> dict[str, str]:
    details = DOCUMENT_GUIDANCE[document_id]
    prompt = f"Explain this optional document in plain language. Why it may be requested: {details['why']} Suggested next step: {details['next']} Mark every requirement as unverified demo guidance."
    return await respond(prompt, history=[], context=context, document_id=document_id)
