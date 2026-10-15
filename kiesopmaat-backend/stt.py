import os
import tempfile

from faster_whisper import WhisperModel

MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
DEVICE = os.getenv("WHISPER_DEVICE", "auto")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "int8")

_model = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
    return _model


def transcribe_bytes(data: bytes, suffix: str = ".webm") -> str:
    # faster-whisper decodeert webm/wav/mp3 zelf via PyAV; ffmpeg is niet nodig.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(data)
        path = f.name
    try:
        segments, _ = _get_model().transcribe(path, language="nl", vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()
    finally:
        os.remove(path)
