"""AI-generated explanations for completed deterministic developer reports."""

import json
from typing import Any

from openai import OpenAI, OpenAIError

from app.config import OPENAI_API_KEY, OPENAI_MODEL


EXPLANATION_INSTRUCTIONS = """You explain a deterministic developer-readiness analysis.
Never calculate, change, or suggest alternative numerical scores. Use only the provided report.
Do not claim that a developer lacks a skill: when evidence is absent, say that no public GitHub evidence was found.
Write a concise explanation with: (1) the strongest evidence, (2) the most important gaps, and
(3) the two highest-impact next actions. Do not invent facts, technologies, or achievements."""


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
            max_output_tokens=600,
            store=False,
        )
    except OpenAIError as error:
        raise ValueError("AI explanations are temporarily unavailable. Please try again later.") from error
    explanation = (response.output_text or "").strip()
    if not explanation:
        raise ValueError("The AI explanation response was empty.")
    return explanation
