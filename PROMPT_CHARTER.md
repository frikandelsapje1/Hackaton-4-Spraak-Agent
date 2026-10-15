# Prompt Charter – Kies op Maat Spraakagent

> Vul de secties hieronder in. Teksten tussen `<...>` zijn invulinstructies; vervang of verwijder ze.

| | |
|---|---|
| **Versie** | 0.1 |
| **Datum** | <datum> |
| **Eigenaar** | <naam> |
| **Status** | Concept |

## 1. Doel en context
- **Doel van de chatbot:** <bijv. de website bedienen via spraak: zoeken, filteren, module openen>
- **Doelgroep:** <studenten die modules kiezen>
- **Waarom een AI-model:** <wat kan regelgebaseerd niet?>
- **Pipeline:** spraak → faster-whisper (tekst) → **prompt/AI-model** → actie/antwoord → frontend

## 2. Rol en persona van het model
- **Rol:** <bijv. behulpzame studieadviseur>
- **Toon en stijl:** <informeel/formeel, kort, Nederlands>
- **Taal:** <Nederlands>

## 3. Taken (wat moet het model kunnen)
| # | Intentie | Voorbeeldzin | Actie in frontend |
|---|----------|--------------|-------------------|
| 1 | Zoeken | "Zoek modules over Python" | `state.q` zetten |
| 2 | Filteren | "Laat alleen masters zien" | filter `level` zetten |
| 3 | Module openen | "Open Cloud Computing" | `openDetail(id)` |
| 4 | Filters wissen | "Begin opnieuw" | reset |
| 5 | Advies geven | "Welke minor past bij mij?" | `recommend`: aanbevolen kaarten tonen |
| 6 | Doorvragen | "Ik wil iets met techniek" | `ask`: één gerichte vervolgvraag |

## 4. Grenzen en regels
- **Mag niet:** <verzinnen van modules, persoonlijke data vragen, ...>
- **Doorvragen:** <welke info is nodig voor een advies (interesses, niveau, EC, plaats, taal, start), hoeveel vragen maximaal, in welke volgorde>
- **Onbekende of onduidelijke invoer:** <om verduidelijking vragen>
- **Buiten scope:** <hoe te reageren>
- **Spraakfouten (STT):** <omgaan met verkeerd verstane woorden, bijv. fuzzy match op modulenamen>

## 5. Invoer voor het model
- **Systeemprompt:** <zie sectie 9>
- **Context die meegegeven wordt:** <lijst met modules, huidige filters, gespreksgeschiedenis>
- **Maximale lengte / aantal beurten geschiedenis:** <...>

## 6. Uitvoerformaat
Het model geeft bij voorkeur gestructureerde output (bijv. JSON) zodat de backend die kan uitvoeren.

```json
{
  "intent": "filter",
  "parameters": { "level": "Master" },
  "reply": "Ik toon nu alleen mastermodules."
}
```
- **Toegestane intents:** <lijst>
- **Validatie in backend:** <schema, fallback bij ongeldige output>

## 7. Voorbeelden (few-shot)
| Gebruiker (STT-tekst) | Verwachte output |
|-----------------------|------------------|
| <...> | <...> |
| <...> | <...> |

## 8. Keuze AI-model
| Criterium | Weging | Model A: <...> | Model B: <...> | Model C: <...> |
|-----------|--------|----------------|----------------|----------------|
| Kwaliteit Nederlands | | | | |
| Structured output / function calling | | | | |
| Latency (spraak vraagt snel) | | | | |
| Kosten | | | | |
| Privacy / dataverwerking (AVG) | | | | |
| Lokaal draaibaar? | | | | |
| **Totaal** | | | | |

**Gekozen model:** <...> **Onderbouwing:** <...>

## 9. Systeemprompt (versie 0.1)
```text
<Plak hier de actuele systeemprompt>
```

## 10. Testen en evalueren
- **Testset:** <aantal zinnen per intentie, inclusief spraakfouten en randgevallen>
- **Succescriteria:** <bijv. ≥ 90% juiste intent, < 2 s antwoordtijd>
- **Testresultaten:** <tabel per promptversie>

## 11. Risico's en ethiek
- **Hallucinaties:** <mitigatie>
- **Privacy (spraakdata, logs):** <wat wordt opgeslagen>
- **Bias / toegankelijkheid:** <...>
- **Prompt injection:** <mitigatie, bijv. outputvalidatie>

## 12. Versiebeheer
| Versie | Datum | Wijziging | Door |
|--------|-------|-----------|------|
| 0.1 | <datum> | Eerste opzet | <naam> |
