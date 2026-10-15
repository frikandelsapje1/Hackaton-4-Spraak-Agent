import json
from pathlib import Path

# Gescrapete data: zet een JSON-lijst met modules in modules.json (naast dit bestand).
# Elke module heeft minimaal "name"; een ontbrekend "id" wordt automatisch toegekend.
DATA_FILE = Path(__file__).with_name("modules.json")


def load_modules() -> list[dict]:
    if not DATA_FILE.exists():
        return FALLBACK_MODULES
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if isinstance(data, dict):  # ondersteunt {"modules": [...]}
        data = data.get("modules", [])
    for i, m in enumerate(data, start=1):
        m.setdefault("id", i)
    return data


# Voorbeelddata, alleen gebruikt als modules.json ontbreekt.
FALLBACK_MODULES = [
    {"id": 1, "name": "Data Analyse met Python", "level": "Bachelor", "theme": "Data & AI", "period": "Periode 1", "ec": 5},
    {"id": 2, "name": "Introductie Machine Learning", "level": "Bachelor", "theme": "Data & AI", "period": "Periode 2", "ec": 5},
    {"id": 3, "name": "Webontwikkeling Fundamentals", "level": "Bachelor", "theme": "Software", "period": "Periode 1", "ec": 5},
    {"id": 4, "name": "Cloud Computing", "level": "Bachelor", "theme": "Infrastructuur", "period": "Periode 3", "ec": 10},
    {"id": 5, "name": "Cybersecurity Basis", "level": "Bachelor", "theme": "Security", "period": "Periode 2", "ec": 5},
    {"id": 6, "name": "Ethisch Hacken", "level": "Master", "theme": "Security", "period": "Periode 4", "ec": 10},
    {"id": 7, "name": "UX Design", "level": "Bachelor", "theme": "Design", "period": "Periode 3", "ec": 5},
    {"id": 8, "name": "Duurzaam Ondernemen", "level": "Bachelor", "theme": "Bedrijf", "period": "Periode 4", "ec": 5},
    {"id": 9, "name": "Spraakgestuurde Interfaces", "level": "Master", "theme": "Data & AI", "period": "Periode 3", "ec": 10},
    {"id": 10, "name": "Projectmanagement Agile", "level": "Bachelor", "theme": "Bedrijf", "period": "Periode 1", "ec": 5},
    {"id": 11, "name": "Databases & SQL", "level": "Bachelor", "theme": "Software", "period": "Periode 2", "ec": 5},
    {"id": 12, "name": "Netwerken & Infrastructuur", "level": "Bachelor", "theme": "Infrastructuur", "period": "Periode 4", "ec": 10},
]

MODULES = load_modules()
