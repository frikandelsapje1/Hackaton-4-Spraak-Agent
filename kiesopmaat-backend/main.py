import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

from modules_data import MODULES
from prompts import ACTION_TOOL, build_system_messages

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MODULE_IDS = {m["id"] for m in MODULES}

app = FastAPI(title="Kies op Maat backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500,http://127.0.0.1:5500").split(","),
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise HTTPException(503, "OPENAI_API_KEY is niet ingesteld (zie .env.example)")
        _client = OpenAI(api_key=key)
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


@app.get("/modules")
def modules():
    return MODULES


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return run_chat(req.text, req.history)


class VoiceResponse(ChatResponse):
    transcript: str


@app.post("/voice", response_model=VoiceResponse)
async def voice(audio: UploadFile = File(...), history: str = Form("[]")):
    data = await audio.read()
    if not data or len(data) > 10_000_000:
        raise HTTPException(400, "Ongeldig audiobestand")
    try:
        turns = [Turn(**t) for t in json.loads(history)[-10:]]
    except Exception:
        raise HTTPException(400, "Ongeldige history")
    from stt import transcribe_bytes  # lazy: model laden pas bij eerste gebruik

    suffix = ".wav" if (audio.content_type or "").endswith("wav") else ".webm"
    text = await run_in_threadpool(transcribe_bytes, data, suffix)
    if not text:
        return VoiceResponse(action="none", reply="Ik heb niets verstaan, probeer het nog eens.", transcript="")
    result = await run_in_threadpool(run_chat, text[:1000], turns)
    return VoiceResponse(**result.model_dump(), transcript=text)


class TranscribeResponse(BaseModel):
    transcript: str


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    # Alleen spraak-naar-tekst, om faster-whisper los van Claude te testen.
    data = await audio.read()
    if not data or len(data) > 10_000_000:
        raise HTTPException(400, "Ongeldig audiobestand")
    from stt import transcribe_bytes

    suffix = ".wav" if (audio.content_type or "").endswith("wav") else ".webm"
    return TranscribeResponse(transcript=await run_in_threadpool(transcribe_bytes, data, suffix))


def run_chat(text: str, history: list[Turn]) -> ChatResponse:
    # Systeemprompt + Prompt Charter worden bij elke aanvraag opnieuw samengesteld.
    messages = build_system_messages() + [t.model_dump() for t in history] + [{"role": "user", "content": text}]
    try:
        resp = client().chat.completions.create(
            model=MODEL,
            max_tokens=600,
            tools=[ACTION_TOOL],
            tool_choice={"type": "function", "function": {"name": "website_actie"}},
            messages=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Fout bij OpenAI: {type(e).__name__}")

    calls = resp.choices[0].message.tool_calls
    if not calls:
        return ChatResponse(action="none", reply="Dat heb ik niet begrepen, kun je het herhalen?")
    try:
        data = json.loads(calls[0].function.arguments)
    except json.JSONDecodeError:
        return ChatResponse(action="none", reply="Dat heb ik niet begrepen, kun je het herhalen?")

    action = data.pop("action", "none")
    reply = data.pop("reply", "")
    # Validatie: nooit onbekende minors doorgeven aan de frontend.
    if action == "open_module" and data.get("module_id") not in MODULE_IDS:
        return ChatResponse(action="none", reply="Die minor ken ik niet. Welke bedoel je?")
    if action == "recommend":
        recs = [
            {"module_id": r["module_id"], "reason": str(r.get("reason", "")).strip()}
            for r in data.get("recommendations", [])
            if isinstance(r, dict) and r.get("module_id") in MODULE_IDS
        ][:5]
        if not recs:
            return ChatResponse(action="none", reply=reply or "Ik kon geen passende minor vinden.")
        data["recommendations"] = recs
    return ChatResponse(action=action, reply=reply, params=data)