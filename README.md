# Kies op Maat – Spraakagent

Prototype (Hackathon 4) van een website voor het kiezen van een minor, die je met spraak bedient en die adviseert via een AI-model.

```
microfoon → faster-whisper (spraak naar tekst) → OpenAI-model → actie op de website
```

Je zegt bijvoorbeeld *"Ik zoek een minor over techniek, HBO, 30 EC"*. De agent stelt zo nodig gerichte vervolgvragen, geeft een advies met per minor een uitleg, en kan filteren, zoeken en minors openen.

## Onderdelen

| Map / bestand | Wat het is |
|---|---|
| `kiesopmaat-frontend/` | Website (HTML, CSS, JavaScript) met chat en microfoonknop |
| `kiesopmaat-backend/` | FastAPI-backend: spraak-naar-tekst, prompt, OpenAI-aanroep |
| `minoren_opgeschoond.json` | Gescrapete data van 74 minors (bron voor site en model) |
| `PROMPT_CHARTER.md` | Sjabloon van de Prompt Charter; wordt als extra systeembericht meegestuurd naar het model |
| `PROMPT_CHARTER_REGELS.md` | Uitgewerkte regels van het model (documentatie) |
| `Test_whisper.py` | Los script om de microfoon en Whisper te proberen |

## Vereisten
- Python 3.12 (andere recente versies werken waarschijnlijk ook)
- Een OpenAI API-key
- Een microfoon en een browser (Chrome of Edge); de microfoon werkt alleen via `localhost`

## Installeren (eenmalig)

```powershell
cd kiesopmaat-backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Maak een bestand `kiesopmaat-backend\.env` met je key (dit bestand staat in `.gitignore`, zet de key nooit in de code of in git):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

De eerste keer dat je spreekt wordt het Whisper-model gedownload; dat duurt even.

## Starten

Je hebt twee vensters nodig.

**1. Backend** (poort 8001):
```powershell
cd kiesopmaat-backend
.\.venv\Scripts\uvicorn main:app --port 8001 --reload
```

**2. Frontend** (poort 8000):
```powershell
cd kiesopmaat-frontend
python -m http.server 8000
```

Open **http://localhost:8000/** in je browser. Gebruik `localhost`, niet `[::]`, en open `index.html` niet rechtstreeks (dan blokkeert de browser de verbinding met de backend).

## Gebruiken

1. Klik rechtsonder op 💬 om de chat te openen.
2. **Typen:** schrijf een bericht en druk op *Stuur*.
3. **Spreken:** klik op 🎤, praat, en klik nog een keer om te stoppen. Je zin verschijnt in de chat en de agent reageert.

Voorbeelden:

| Zeg of typ | Wat er gebeurt |
|---|---|
| "Welke minor past bij mij?" | De agent stelt een gerichte vraag |
| "Ik hou van techniek, HBO, 30 EC" | Advies met kaarten en per minor een *Waarom aanbevolen* |
| "Laat alleen WO zien" | Filter wordt toegepast |
| "Zoek naar communicatie" | Zoekopdracht wordt ingevuld |
| "Open Da Vinci" | Detailvenster van die minor |
| "Begin opnieuw" | Filters en zoekopdracht worden gewist |

### Alleen de spraak testen (zonder AI-model)
Open **http://localhost:8000/?stt=1**. De microfoon laat dan alleen zien wat Whisper verstaat; er wordt niets naar OpenAI gestuurd. Handig als je nog geen key hebt.

### Een andere backend-poort
Draait de backend elders, open dan `http://localhost:8000/?api=http://localhost:9000`.

## De prompt testen
Een testset met 10 zinnen (doorvragen, advies, filteren, buiten scope, beschermde kenmerken, persoonsgegevens):
```powershell
cd kiesopmaat-backend
.\.venv\Scripts\python test_prompt.py
```
Dit roept het echte model aan en kost een paar cent. De uitkomst kan per keer verschillen; lees de antwoorden en kijk niet alleen naar OK of FAIL.

## Configuratie

Alles is via `kiesopmaat-backend\.env` in te stellen.

| Variabele | Standaard | Betekenis |
|---|---|---|
| `OPENAI_API_KEY` | – | Verplicht voor advies en chat |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Welk model wordt gebruikt |
| `CATALOG_SUMMARY_CHARS` | `150` | Lengte van de samenvatting per minor die het model ziet (meer = beter advies, maar meer tokens) |
| `WHISPER_MODEL` | `small` | Whisper-formaat (`tiny`, `base`, `small`, `medium`, …) |
| `WHISPER_DEVICE` | `auto` | `cpu` of `cuda` |
| `WHISPER_COMPUTE` | `int8` | Bij GPU bijvoorbeeld `float16` |
| `CHARTER_FILE` | `PROMPT_CHARTER.md` | Ander bestand voor het charter-bericht |
| `MODULES_FILE` | `minoren_opgeschoond.json` | Ander databestand |
| `CORS_ORIGINS` | localhost:8000, 5500 | Toegestane websiteadressen, gescheiden door komma's |

## Hoe het werkt

- **Data:** `modules_data.py` leest de JSON en haalt er niveau, EC, thema's, plaats, taal, vorm, periodes en een samenvatting uit.
- **Prompt:** `prompts.py` bevat de systeemprompt met de regels en een compacte catalogus (één regel per minor, ~6.300 tokens). De vaste prompt is ongeveer 8.500 tokens per aanvraag. Het model antwoordt altijd via één functie, `website_actie`, met een vast schema.
- **Acties:** `recommend`, `ask`, `search`, `filter`, `open_module`, `reset`, `sort`, `none`.
- **Controle in de backend:** id's van minors die niet bestaan worden niet doorgegeven aan de website.
- **Geschiedenis:** de frontend stuurt de laatste 10 berichten mee; de backend bewaart niets.

### API

| Endpoint | Doel |
|---|---|
| `GET /health` | Controle dat de backend draait |
| `GET /modules` | Alle minors met details (voor de website) |
| `POST /chat` | `{"text": "...", "history": [...]}` → actie en antwoord |
| `POST /voice` | Audio (formulier) → transcriptie, actie en antwoord |
| `POST /transcribe` | Alleen audio naar tekst (zonder AI-model) |

Interactieve documentatie: http://localhost:8001/docs

## Privacy en veiligheid
- Whisper draait lokaal; audio wordt na transcriptie direct verwijderd.
- De tekst van de student gaat wel naar OpenAI. Er wordt **nog niet** automatisch gefilterd op persoonsgegevens; dat staat als instructie in de prompt en als open punt in `PROMPT_CHARTER_REGELS.md`. Gebruik in het prototype alleen synthetische gegevens.
- Zet je API-key alleen in `.env`.

## Problemen oplossen

| Probleem | Oplossing |
|---|---|
| `{"detail":"Not Found"}` in de browser | Je zit op poort 8001 (de backend). Open de website op poort 8000. |
| `ERR_ADDRESS_INVALID` bij `[::]:8000` | Typ zelf `http://localhost:8000/` |
| "Kan de minors niet laden" | De backend draait niet op poort 8001 |
| `Error loading ASGI app` | Start uvicorn vanuit de map `kiesopmaat-backend` |
| 503 `OPENAI_API_KEY is niet ingesteld` | `.env` ontbreekt of staat in de verkeerde map; herstart uvicorn |
| 502 `Fout bij OpenAI` | Key ongeldig, geen tegoed of rate limit; zie de uvicorn-uitvoer |
| 500 bij spraak: `open() got an unexpected keyword argument 'metadata_errors'` | Te nieuwe PyAV: `pip install "av>=14,<16"` (staat al in `requirements.txt`) |
| Geen microfoon | Gebruik `localhost` en geef de browser toestemming |
| Eerste spraak duurt lang | Whisper-model wordt gedownload |

## Nog te doen
- Filter voor persoonsgegevens vóór de aanroep naar OpenAI
- Beslissen over verwerkersovereenkomst en bewaartermijn bij OpenAI
- Modelkeuze onderbouwen en de Prompt Charter invullen
- De crawler (`kiesopmaat-crawler/`) is nog leeg
