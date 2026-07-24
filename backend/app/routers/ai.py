"""AI content assistance for editors — uses Emergent Universal LLM Key.

Kept modular: if key or provider is missing, gracefully returns 501 so the frontend
can render 'AI Assist coming soon'. When available uses `emergentintegrations`."""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..deps import require_admin

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AssistPayload(BaseModel):
    task: str  # summarize | expand | headline | meta_description | rewrite
    text: str
    tone: Optional[str] = "editorial"


PROMPTS = {
    "summarize": "Summarize the following article in 3 concise, editorial-style sentences suitable for a magazine excerpt:\n\n{text}",
    "expand": "Expand the following idea into a polished 200-word editorial paragraph in a luxury travel magazine tone:\n\n{text}",
    "headline": "Craft 5 elegant, magazine-style headlines (max 10 words each) for the following content. Return as a numbered list:\n\n{text}",
    "meta_description": "Write an SEO meta description (max 155 chars, compelling, single sentence) for:\n\n{text}",
    "rewrite": "Rewrite the following in a polished editorial tone matching Condé Nast Traveller / Forbes style. Preserve meaning:\n\n{text}",
}


@router.post("/assist")
async def assist(payload: AssistPayload, _u=Depends(require_admin())):
    prompt_tpl = PROMPTS.get(payload.task)
    if not prompt_tpl:
        raise HTTPException(400, "Unknown task")

    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        raise HTTPException(501, "AI not configured: EMERGENT_LLM_KEY missing")

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage  # type: ignore
    except Exception as exc:
        raise HTTPException(501, f"AI library unavailable: {exc}")

    prompt = prompt_tpl.format(text=payload.text)
    try:
        chat = (
            LlmChat(api_key=key, session_id="musafir-editor", system_message="You are a luxury travel magazine editor.")
            .with_model("anthropic", "claude-sonnet-4-5-20250929")
        )
        resp = await chat.send_message(UserMessage(text=prompt))
        return {"result": str(resp)}
    except Exception as exc:
        raise HTTPException(502, f"AI request failed: {exc}")
