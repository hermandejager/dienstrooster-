# Dienstrooster Generator

Een uitgebreide Flask-applicatie voor het genereren, analyseren en exporteren van een 3‑maanden dienstrooster (Dag / Avond / Nacht) met eerlijke verdeling, voorkeuren en exports.

## Features

- 3 maanden (rolling) rooster generatie met fairness heuristiek
	- Balanceert totaal aantal diensten
	- Nachtlimiet per medewerker + geen dag direct na nacht + max 2 nachten op rij
	- Voorkeur-diensten (weging)
	- Beschikbaarheden blokkeren selectie
- Medewerkersbeheer (CRUD) + voorkeuren + beschikbaarheid + max nachten/maand
- Material Design UI (filters, statistieken, matrixweergave: medewerkers verticaal / dagen horizontaal)
- Exports: JSON, CSV, PDF
- Authenticatie (simple) + routeprotectie
- Automatische migratie oud medewerkers-formaat -> nieuw objectmodel

## Snel Starten

## Installatie

Zorg dat Python 3.10+ is geïnstalleerd.

```powershell
pip install -r requirements.txt
python app.py
```

Open daarna in de browser:
```
http://127.0.0.1:5000
```

## Functionaliteit Overzicht
| Domein | Mogelijkheden |
|--------|---------------|
| Generatie | 3 maanden, fairness, voorkeuren, beschikbaarheid |
| UI | Filters (medewerker, dienst, datumbereik, zoek), statistieken, matrixlayout |
| Beheer | Medewerkers toevoegen, bewerken (voorkeuren / beschikbaarheid / nachtlimaat), verwijderen |
| Export | JSON API, CSV download, PDF (ReportLab) |
| Security | Login vereist voor genereren, beheer, exports |
| Migratie | Automatische detectie legacy `medewerkers.json` lijst en conversie |

## Routes (kern)
| Route | Methode(n) | Beschrijving |
|-------|------------|--------------|
| `/` | GET/POST | Start + rooster genereren |
| `/rooster` | GET | Weergave (matrix) |
| `/api/rooster` | GET | JSON data (readonly) |
| `/export/rooster.(json|csv|pdf)` | GET | Exports (auth vereist) |
| `/medewerkers` | GET/POST | Overzicht + toevoegen |
| `/medewerker/<naam>` | GET/POST | Bewerken medewerker |
| `/verwijder_medewerker/<naam>` | POST | Verwijderen |
| `/login` | GET/POST | Inloggen |
| `/logout` | GET | Uitloggen |

## Structuur
```
app.py                # Flask app + scheduling + routes
templates/            # Jinja templates (Material Design)
  base.html
  index.html
  rooster.html        # Matrix weergave
  medewerkers*.html
requirements.txt      # Dependencies (Flask, reportlab)
medewerkers.json      # (Genegeerd in git) lokale data
ruff.toml             # Lint / style configuratie
Dockerfile            # Container build
docker-compose.yml    # Gemak: run + volume mount data
scripts/
  gen_secret.py       # Genereer SECRET_KEY en optioneel admin wachtwoord hash
docs/
  overview.md         # Architectuur / uitleg
.github/workflows/ci.yml  # CI pipeline
.tests/
  test_smoke.py
  test_fairness.py
.env.example          # Voorbeeld env variabelen
.gitignore            # Sluit gevoelige / lokale bestanden uit
```

## Testen van basis
1. Start zonder medewerkers (rooster toont '-').
2. Voeg medewerkers toe via "Beheer medewerkers".
3. Genereer een nieuw rooster.
4. Controleer dat namen rouleren.

## Werken met een virtual environment (aanrader)

1. Installeer (indien nodig) Python via winget:
```powershell
winget install -e --id Python.Python.3.12
```
2. Controleer installatie:
```powershell
python --version
```
3. Maak en activeer een virtual environment in de projectmap:
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./.venv/Scripts/Activate.ps1
```
4. Installeer dependencies binnen de venv:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
5. Start de app:
```powershell
python app.py
```
6. Deactiveer venv (optioneel):
```powershell
deactivate
```

Let op: Activeer de venv opnieuw in elke nieuwe terminal sessie met:
```powershell
./.venv/Scripts/Activate.ps1
```

## Config & Gegevens
| Item | Locatie | Opmerking |
|------|---------|-----------|
| Secret key | `.env` (`SECRET_KEY`) | Genereer lange random waarde |
| Medewerkersdata | `medewerkers.json` | Wordt gemigreerd naar objectstructuur bij laden |
| Login | ROLES dict (admin pw uit `.env`) | Gebruik echte user storage in prod |

## Fairness Heuristiek (vereenvoudigd)
1. Filter kandidaten op beschikbaarheid + limieten.
2. Verwerp kandidaat indien: dagdienst na eigen nachtdienst vorige dag of >2 nachten op rij.
3. Sorteer op: (totaal diensten, diensten van dit type, negatieve voorkeur-score, random tiebreaker)
4. Kies eerste.

## Export Formaten
| Formaat | Inhoud | Doel |
|---------|--------|------|
| JSON | Lijst dagen met per dienst medewerker | Integratie / API |
| CSV | Tabulaire dataset | Spreadsheet analyse |
| PDF | Tabel per maand (basis) | Print / sharing |

## Security Notities
- Alleen eenvoudige session + plaintext secret → vervang voor productie.
- Voeg CSRF bescherming toe als je formulieren uitbreidt (Flask-WTF).
- Overweeg wachtwoord reset / user beheer interface.

## Roadmap (kort)
- [x] CI workflow (pytest smoke + fairness tests)
- [x] Linting (ruff) + in CI
- [x] Dockerfile + docker-compose
- [x] Config via `.env` (python-dotenv)
- [x] Fairness constraints (nacht + dag-na-nacht + max 2 nachten + weeklimiet)
- [ ] Extra rustregels (min uren tussen late -> vroege dienst)
- [ ] Kalender UI beschikbaarheid
- [ ] Role-based authorisatie (admin / viewer)
- [ ] Persistente database (PostgreSQL/SQLite) optie

## Licentie
Kies een licentie (MIT aanbevolen). Voeg een `LICENSE` bestand toe.

## Versiebeheer / Release
Tag een release:
```powershell
git tag -a v0.1.0 -m "Initial public version"
git push origin v0.1.0
```

Volgende patch release voorbeeld:
```powershell
git tag -a v0.1.1 -m "Docker + env + tests"
git push origin v0.1.1
```

## Docker
Build & run lokaal:
```powershell
docker build -t dienstrooster:latest .
copy .env.example .env  # pas waarden aan
docker run --rm -p 5000:5000 --env-file .env dienstrooster:latest
```

## Bijdragen
Maak een branch, open een Pull Request. Houd commits klein en beschrijvend.

## Problemen / Feedback
Open een Issue met reproduceerbare stappen of gewenste feature.

## Branch Protection Aanpak
1. Ga naar GitHub repo Settings -> Branches.
2. Add rule: branch name pattern `main`.
3. Vink aan: Require pull request reviews (min 1), Require status checks.
4. Selecteer checks: `ruff` (lint), `pytest` (tests / fairness), eventueel `build`.
5. Optioneel: Require signed commits, linear history.
6. Save.

## Tests Uitvoeren
```powershell
# In venv
pytest -q
```
Rapporteert fairness regels en basis smoke.

## Geheimen Genereren
```powershell
python scripts/gen_secret.py --admin-password NieuweSterkePW123!
```
Output kopiëren naar `.env` (vervang bestaande waarden).

