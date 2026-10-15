import json

from modules_data import MODULES

# Zie PROMPT_CHARTER.md voor de bedoeling; pas hier de prompt aan.
SYSTEM_PROMPT = """Je bent de spraakassistent van de website Kies op Maat, waar studenten modules kiezen.
Je krijgt tekst die uit spraak is omgezet (speech-to-text) en kan fouten bevatten; match modulenamen daarom op gelijkenis.
Antwoord in het Nederlands, kort en vriendelijk.

Je bestuurt de website uitsluitend via de tool `website_actie`. Roep deze tool altijd precies één keer aan.
Acties:
- search: zoekterm instellen (query)
- filter: filters instellen (level, theme, period, ec); alleen de genoemde velden invullen
- open_module: een module openen (module_id uit de lijst)
- reset: alle filters en zoekopdracht wissen
- sort: sorteren op name, ec of period
- none: de vraag is onduidelijk of buiten scope; stel in `reply` een verduidelijkende vraag

Verzin nooit modules; gebruik alleen de lijst hieronder.

Beschikbare modules:
{modules}
"""


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(modules=json.dumps(MODULES, ensure_ascii=False))


ACTION_TOOL = {
    "name": "website_actie",
    "description": "Voer een actie uit op de Kies op Maat website en geef een antwoord aan de gebruiker.",
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["search", "filter", "open_module", "reset", "sort", "none"]},
            "query": {"type": "string"},
            "level": {"type": "string", "enum": ["Bachelor", "Master"]},
            "theme": {"type": "string"},
            "period": {"type": "string"},
            "ec": {"type": "integer"},
            "module_id": {"type": "integer"},
            "sort_by": {"type": "string", "enum": ["name", "ec", "period"]},
            "reply": {"type": "string", "description": "Antwoord aan de gebruiker"},
        },
        "required": ["action", "reply"],
    },
}
