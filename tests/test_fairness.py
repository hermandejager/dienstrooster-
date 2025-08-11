import re
from datetime import datetime
from app import genereer_rooster, DIENSTEN


def test_no_day_after_own_night():
    medewerkers = [
        {"naam": "A", "voorkeur_diensten": [], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 10, "max_diensten_per_week": 10},
        {"naam": "B", "voorkeur_diensten": [], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 10, "max_diensten_per_week": 10},
    ]
    rooster = genereer_rooster(datetime(2025, 1, 1), medewerkers, DIENSTEN, maanden=1, fair=True)
    by_date = {r['datum']: r for r in rooster}
    previous = None
    for r in rooster:
        if previous and previous.get('Nachtdienst') != '-' and previous.get('Nachtdienst') == r.get('Dagdienst'):
            raise AssertionError("Dagdienst direct na eigen Nachtdienst gevonden op %s" % r['datum'])
        previous = r


def test_max_two_consecutive_nights():
    medewerkers = [
        {"naam": "A", "voorkeur_diensten": ["Nachtdienst"], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 31, "max_diensten_per_week": 21},
        {"naam": "B", "voorkeur_diensten": ["Nachtdienst"], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 31, "max_diensten_per_week": 21},
        {"naam": "C", "voorkeur_diensten": ["Nachtdienst"], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 31, "max_diensten_per_week": 21},
    ]
    rooster = genereer_rooster(datetime(2025, 1, 1), medewerkers, DIENSTEN, maanden=1, fair=True)
    consec = 0
    last_person = None
    for r in rooster:
        nd = r.get('Nachtdienst')
        if nd == '-' or nd is None:
            consec = 0
            last_person = None
            continue
        if nd == last_person:
            consec += 1
            assert consec <= 2, f"Meer dan 2 nachtdiensten op rij voor {nd}"
        else:
            consec = 1
            last_person = nd


def test_balances_distribution():
    medewerkers = [
        {"naam": "A", "voorkeur_diensten": [], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 10, "max_diensten_per_week": 10},
        {"naam": "B", "voorkeur_diensten": [], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 10, "max_diensten_per_week": 10},
        {"naam": "C", "voorkeur_diensten": [], "beschikbaarheid": {}, "max_nachtdiensten_per_maand": 10, "max_diensten_per_week": 10},
    ]
    rooster = genereer_rooster(datetime(2025, 1, 1), medewerkers, DIENSTEN, maanden=1, fair=True)
    counts = {m['naam']: 0 for m in medewerkers}
    for r in rooster:
        for d in DIENSTEN:
            naam = r.get(d)
            if naam and naam != '-':
                counts[naam] += 1
    values = list(counts.values())
    assert max(values) - min(values) <= 5, f"Distributie uit balans: {counts}"
