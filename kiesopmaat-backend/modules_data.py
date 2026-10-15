import json
import os
import re
from pathlib import Path

# Bron: gescrapete minors. Elk item heeft {"minor": naam, "tekst": vrije tekst}.
DATA_FILE = Path(os.getenv("MODULES_FILE", Path(__file__).resolve().parent.parent / "minoren_opgeschoond.json"))

BULLET = "\u2022"


def _field(text: str, label: str) -> str:
    m = re.search(rf"^{BULLET}\s*{re.escape(label)}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def _section(text: str, start: str, max_chars: int) -> str:
    m = re.search(rf"^{re.escape(start)}\s*\n(.*?)(?=\n(?:Leerdoelen|Ingangseisen|Literatuur|Rooster|Toetsing|Aanvullende informatie)\s*\n|\Z)", text, re.M | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip()[:max_chars] if m else ""


def _periods(text: str) -> list[str]:
    m = re.search(rf"{BULLET}\s*Onderwijsperiodes:\s*\n(.*?)(?=\n{BULLET}|\Z)", text, re.S)
    return [l.strip() for l in m.group(1).splitlines() if l.strip()] if m else []


def parse_minor(item: dict, idx: int) -> dict:
    text = item.get("tekst", "")
    ec = _field(text, "Aantal EC").replace(",0", "")
    lines = [l.strip() for l in text.splitlines()]
    intro = " ".join(l for l in lines[1:] if l and not l.startswith(BULLET))
    intro = intro.split("Leerdoelen")[0]
    return {
        "id": idx,
        "name": item.get("minor", "").strip(),
        "level": _field(text, "Niveau"),
        "ec": int(ec) if ec.isdigit() else ec,
        "themes": [t.strip() for t in _field(text, "Thema's").split(",") if t.strip()],
        "place": _field(text, "Plaats").title(),
        "language": _field(text, "Voertaal"),
        "form": _field(text, "Onderwijsvorm"),
        "type": _field(text, "Type"),
        "program": _field(text, "Opleiding"),
        "periods": _periods(text),
        "summary": re.sub(r"\s+", " ", intro).strip()[:600],
        "entry": _section(text, "Ingangseisen", 300),
    }


def load_modules() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("modules", [])
    return [parse_minor(m, i) for i, m in enumerate(data, start=1)]


MODULES = load_modules()
