"""AI-generated explanations for completed deterministic developer reports."""

import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, OPENAI_MODEL


EXPLANATION_INSTRUCTIONS = """You explain a deterministic developer-readiness analysis.
Never calculate, change, or suggest alternative numerical scores. Use only the provided report.
Do not claim that a developer lacks a skill: when evidence is absent, say that no public GitHub evidence was found.
Write no more than six short sentences covering: (1) the strongest evidence, (2) the most important gaps,
and (3) the two highest-impact next actions. Do not invent facts, technologies, or achievements."""


def _extract_output_text(response: Any) -> str:
    """Read text from SDK convenience output or the underlying message content."""
    convenience_text = getattr(response, "output_text", "") or ""
    if convenience_text.strip():
        return convenience_text.strip()

    text_parts = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                text = getattr(content, "text", "") or ""
                if text.strip():
                    text_parts.append(text.strip())
    return "\n".join(text_parts).strip()


def generate_ai_explanation(
    developer_report: dict[str, Any], client: Any | None = None
) -> str:
    """Return a natural-language explanation while preserving deterministic results."""
    if client is None:
        if not OPENAI_API_KEY:
            raise ValueError("AI explanations are unavailable because OPENAI_API_KEY is not configured.")
        client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=EXPLANATION_INSTRUCTIONS,
            input=json.dumps(developer_report),
            # This cap includes hidden reasoning tokens as well as visible text.
            # Minimal reasoning is sufficient because the report is already scored.
            max_output_tokens=1600,
            reasoning={"effort": "minimal"},
            store=False,
        )
    except OpenAIError as error:
        raise ValueError("AI explanations are temporarily unavailable. Please try again later.") from error
    if getattr(response, "status", "completed") != "completed":
        reason = getattr(getattr(response, "incomplete_details", None), "reason", None)
        suffix = f" ({reason})" if reason else ""
        raise ValueError(f"AI explanations are temporarily unavailable{suffix}. Please try again later.")

    explanation = _extract_output_text(response)
    if not explanation:
        raise ValueError("The AI explanation response was empty.")
    return explanation
