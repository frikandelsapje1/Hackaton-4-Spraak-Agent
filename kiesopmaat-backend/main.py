import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from modules_data import MODULES
from prompts import ACTION_TOOL, build_system_prompt

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")
MODULE_IDS = {m["id"] for m in MODULES}

app = FastAPI(title="Kies op Maat backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_client = None


def client() -> Anthropic:
    global _client
    if _client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise HTTPException(503, "ANTHROPIC_API_KEY is niet ingesteld (zie .env.example)")
        _client = Anthropic(api_key=key)
    return _client


class Turn(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)  # tekst uit faster-whisper
    history: list[Turn] = Field(default_factory=list, max_length=10)


class ChatResponse(BaseModel):
    action: str
    reply: str
    params: dict = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [t.model_dump() for t in req.history] + [{"role": "user", "content": req.text}]
    try:
        resp = client().messages.create(
            model=MODEL,
            max_tokens=400,
            # Caching maakt een grote modulelijst goedkoper en sneller bij herhaalde vragen.
            system=[{"type": "text", "text": build_system_prompt(), "cache_control": {"type": "ephemeral"}}],
            tools=[ACTION_TOOL],
            tool_choice={"type": "tool", "name": ACTION_TOOL["name"]},
            messages=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Fout bij Claude: {type(e).__name__}")

    block = next((b for b in resp.content if b.type == "tool_use"), None)
    if block is None:
        return ChatResponse(action="none", reply="Dat heb ik niet begrepen, kun je het herhalen?")

    data = dict(block.input)
    action = data.pop("action", "none")
    reply = data.pop("reply", "")
    # Validatie: nooit een onbekende module doorgeven aan de frontend.
    if action == "open_module" and data.get("module_id") not in MODULE_IDS:
        return ChatResponse(action="none", reply="Die module ken ik niet. Welke bedoel je?")
    return ChatResponse(action=action, reply=reply, params=data)