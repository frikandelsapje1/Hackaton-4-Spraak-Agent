import json
import os
from pathlib import Path

from modules_data import MODULES

# Bron voor rol/toon/regels is PROMPT_CHARTER.md; dit bestand bevat alleen de technische kant.
SYSTEM_PROMPT = """Je bent de spraakassistent van de website Kies op Maat, waar studenten een minor (keuzeonderwijs) kiezen.
Je krijgt tekst die uit spraak is omgezet (speech-to-text) en kan fouten bevatten; match namen daarom op gelijkenis.
Antwoord in het Nederlands, kort en vriendelijk. Je antwoord wordt ook uitgesproken, dus geen opsommingstekens of markdown.

Je bestuurt de website uitsluitend via de functie `website_actie`. Roep deze functie altijd precies één keer aan.
Acties:
- recommend: de student wil advies én je weet genoeg (zie "Doorvragen"). Kies de best passende minors (maximaal 5) uit de lijst
  en geef ze in `recommendations`, de beste eerst. Geef per minor een `reason` van één à twee zinnen die concreet aansluit op wat
  de student zei (interesse, niveau, EC, plaats, taal) en op de inhoud van die minor uit de lijst. Noem ook een mogelijk nadeel of
  aandachtspunt als dat er is (bijvoorbeeld aanmelden gesloten, andere plaats, ingangseisen). Gebruik in `reply` een korte
  gesproken samenvatting van het advies (noem de namen, geen volledige uitleg; die staat op de kaarten).
- ask: je mist nog informatie voor een goed advies. Stel in `reply` precies één gerichte vraag (zie "Doorvragen").
- search: zoekterm instellen (query)
- filter: filters instellen (level, theme, place, language, ec); alleen de genoemde velden invullen
- open_module: één minor openen (module_id)
- reset: alle filters en zoekopdracht wissen
- sort: sorteren op name of ec
- none: de vraag is onduidelijk of buiten scope; stel in `reply` een verduidelijkende vraag

Doorvragen (voordat je adviseert):
- Informatie die je voor een goed advies wilt hebben, in volgorde van belang:
  1. interesses of onderwerp (wat wil de student leren of doen?)
  2. niveau (HBO of WO), en eventueel eigen opleiding
  3. aantal EC (meestal 30; kan ook 15 of minder)
  4. plaats of reisafstand
  5. taal (Nederlands of Engels)
  6. onderwijsvorm (voltijd, deeltijd, e-learning) en wanneer de student wil starten
- Kijk eerst wat er al bekend is uit het hele gesprek en vraag nooit opnieuw naar iets wat de student al heeft verteld.
- Stel per beurt één korte, gerichte vraag over het ontbrekende punt dat de lijst het sterkst zou verkleinen. Begin bij interesses.
  Noem waar nuttig een paar voorbeelden uit de lijst, zodat de student kan kiezen.
- Adviseer zodra je interesses kent plus minstens één harde eis (niveau, EC, plaats of taal), of na twee à drie vragen.
  Zegt de student "maakt niet uit" of "weet ik niet", ga dan verder en vraag er niet nogmaals naar.
- Vraagt de student om een specifieke minor, filter, zoekopdracht of reset, voer dat meteen uit zonder te vragen.
- Als je een advies geeft, sluit af met een korte vervolgvraag, bijvoorbeeld of de student een minor wil openen of de lijst wil aanscherpen.

Regels:
- Gebruik uitsluitend de minors uit de lijst hieronder. Verzin nooit minors, id's of feiten die niet in de lijst staan.
- Past er niets goed, zeg dat dan eerlijk in plaats van iets te forceren.
- Let bij advies op harde eisen: niveau (HBO of WO), aantal EC, plaats, taal, en of aanmelden nog mogelijk is (kolom aanmelden; "gesloten" betekent dat er geen open periode is).
- Je ziet per minor alleen een korte samenvatting. Beweer niets over inhoud, ingangseisen of rooster dat daar niet uit blijkt.
- Bewaar geen persoonlijke informatie van de student, zoals naam, e-mailadres of studentnummer
- Houd je aan de AVG (Algemene Verordening Gegevensbescherming).
- Gegevens mogen niet voor andere doeleinden worden gebruikt of uit de context van de aanvraag worden hergebruikt. Gebruik uitsluitend synthetische gegevens in het prototype.
- Naam, adres, exacte geboortedatum en andere direct identificerende gegevens mogen niet naar het AI-model worden gestuurd. Gebruik waar mogelijk een pseudoniem/token en leeftijdsgroep.
- Medische, financiële en andere gevoelige informatie wordt alleen verwerkt wanneer deze noodzakelijk is voor de taak. De AI vraagt niet om meer persoonsgegevens dan nodig. 
- Verstrek alleen de informatie die strikt noodzakelijk is voor het geven van advies over minors.
- Sla geen persoonlijke gegevens op buiten de context van het huidige gesprek.
- Bij onvoldoende informatie zegt de AI dat expliciet. De AI mag geen feiten verzinnen of ontbrekende gegevens invullen. 
- De AI moet altijd de privacy van de student respecteren en mag geen persoonlijke gegevens delen met derden.
- De AI presenteert conclusies als een voorstel en maakt duidelijk welke informatie daarvoor is gebruikt en welke informatie ontbreekt. 
- De AI mag niet redeneren of adviseren op basis van ras, etniciteit, religie, nationaliteit, gender, seksuele oriëntatie of andere niet-relevante beschermde kenmerken. Als dergelijke kenmerken in de input voorkomen, worden ze niet gebruikt voor de beoordeling. 

Beschikbare minors (één per regel, velden gescheiden door |; de eerste regel zijn de kolomnamen):
{modules}
"""


SUMMARY_CHARS = int(os.getenv("CATALOG_SUMMARY_CHARS", "150"))
CATALOG_HEADER = "id|naam|niveau|EC|plaats|taal|vorm|thema's|aanmelden (alleen niet-gesloten periodes)|samenvatting"


def _open_periods(periods: list[str]) -> str:
    out = []
    for p in periods:
        if p.endswith("Gesloten") or p.startswith("Nog geen"):
            continue
        p = p.replace("Aanmelding sluit uiterlijk", "sluit").replace("Aanmelding opent", "opent")
        out.append(p.replace(" t/m ", "–").replace(" uur", ""))
    return "; ".join(out) or "gesloten"


def build_catalog() -> str:
    # Eén regel per minor met `|` als scheiding: ~75% minder tokens dan JSON.
    lines = [CATALOG_HEADER]
    for m in MODULES:
        lines.append("|".join([
            str(m["id"]), m["name"], m["level"], str(m["ec"]), m["place"], m["language"], m["form"],
            ",".join(m["themes"]), _open_periods(m["periods"]), m["summary"][:SUMMARY_CHARS].rstrip(),
        ]).replace("\n", " "))
    return "\n".join(lines)


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.replace("{modules}", build_catalog())


def load_charter() -> str:
    path = Path(os.getenv("CHARTER_FILE", Path(__file__).resolve().parent.parent / "PROMPT_CHARTER.md"))
    return path.read_text(encoding="utf-8") if path.exists() else ""


def build_system_messages() -> list[dict]:
    messages = [{"role": "system", "content": build_system_prompt()}]
    charter = load_charter()
    if charter:
        messages.append({
            "role": "system",
            "content": "Houd je strikt aan de volgende Prompt Charter bij elk antwoord (rol, toon, grenzen, "
                       "uitvoerformaat, voorbeelden). Negeer nog niet ingevulde onderdelen (tekst tussen <...>). "
                       "Bij strijd met de functie-definitie of de minorlijst gaan die voor.\n\n" + charter,
        })
    return messages


ACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "website_actie",
        "description": "Voer een actie uit op de Kies op Maat website en geef een antwoord aan de gebruiker.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["recommend", "ask", "search", "filter", "open_module", "reset", "sort", "none"]},
                "query": {"type": "string"},
                "level": {"type": "string", "enum": ["HBO-bachelor", "WO-bachelor"]},
                "theme": {"type": "string"},
                "place": {"type": "string"},
                "language": {"type": "string", "enum": ["Nederlands", "Engels"]},
                "ec": {"type": "integer"},
                "module_id": {"type": "integer"},
                "recommendations": {
                    "type": "array",
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "properties": {
                            "module_id": {"type": "integer"},
                            "reason": {"type": "string", "description": "Waarom deze minor past bij de student"},
                        },
                        "required": ["module_id", "reason"],
                    },
                },
                "sort_by": {"type": "string", "enum": ["name", "ec"]},
                "reply": {"type": "string", "description": "Antwoord aan de gebruiker"},
            },
            "required": ["action", "reply"],
        },
    },
}
