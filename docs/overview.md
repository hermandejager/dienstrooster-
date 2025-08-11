# Architectuur Overzicht

## Componenten
- Flask applicatie (`app.py`): routing, planning algoritme, authenticatie, exports.
- Templates: Material Design UI (Jinja) voor genereren en inspectie.
- Data opslag: `medewerkers.json` (lokaal bestand, geen DB voor demo).
- Planning algoritme: fairness heuristiek met limieten (nacht / week) en voorkeuren.
- Exports: JSON (API), CSV, PDF (ReportLab).
- Configuratie: `.env` geladen via `python-dotenv`.
- CI: GitHub Actions workflow (`.github/workflows/ci.yml`) voert lint + tests uit.
- Containerisatie: `Dockerfile` + optionele `docker-compose.yml` (volume voor data).

## Datamodel (vereenvoudigd)
```json
{
  "naam": "Alice",
  "voorkeur_diensten": ["Dagdienst"],
  "beschikbaarheid": { "2025-08-12": true, "2025-08-15": false },
  "max_nachtdiensten_per_maand": 6,
  "max_diensten_per_week": 7
}
```

## Generatie Stappen
1. Itereer over dagen binnen de periode (3 maanden ≈ 90 dagen).
2. Voor elke dienst:
   - Filter medewerkers op beschikbaarheid en limieten.
   - Pas regels toe (geen dag na eigen nacht, max 2 nachten op rij, weeklimiet, nachtlimiet).
   - Sorteer kandidaten op (totaal diensten, diensten van dit type, voorkeur-score, random tiebreak).
   - Kies eerste kandidaat en update counters.
3. Bewaar resultaatlijst in sessie.

## Beveiliging
- Eenvoudige login (enkel admin user) met password hash.
- Sessiesleutel uit `.env`.
- Geen CSRF of rollenbeheer beyond admin (roadmap).

## Uitbreidingsideeën
- Postgres / SQLite opslag.
- UI voor kalender beschikbaarheid.
- Hardere constraints (min rusturen / weekendregels).
- Meerdere gebruikers + rolgebaseerde rechten.
- Betere PDF layout (paginerende tabellen per maand en styling).

## Deploy Indicaties
- Production WSGI server (gunicorn) + reverse proxy (nginx) voor echte deployment.
- Externe secrets management (Azure Key Vault / Vault) i.p.v. `.env` in image.
