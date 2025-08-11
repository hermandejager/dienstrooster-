# Dienstrooster Generator

Een eenvoudige Flask-applicatie om een 3-maanden dienstrooster te genereren voor zorgmedewerkers (dag, avond, nacht).

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

## Functionaliteit
- Genereer een rooster over ~90 dagen.
- Dag-, Avond- en Nachtdienst elke dag.
- Medewerkers toevoegen en verwijderen via /medewerkers.
- Rooster tonen via /rooster.

## Structuur
- `app.py` — Flask applicatie + logica.
- `templates/` — HTML templates.
- `medewerkers.json` — Opslag medewerkerslijst.

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

## Volgende uitbreidingen (mogelijk)
- Beschikbaarheden en voorkeuren per medewerker.
- Eerlijke verdeling (balanceren nachtdiensten).
- Export naar CSV / PDF.
- Inloggen / rollen.
