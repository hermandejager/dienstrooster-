from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, Response, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

import random
from datetime import datetime, timedelta
import json
import os


app = Flask(__name__)
app.secret_key = 'dienstrooster_secret_key'

MEDEWERKERS_FILE = os.path.join(os.path.dirname(__file__), 'medewerkers.json')
DIENSTEN = ['Dagdienst', 'Avonddienst', 'Nachtdienst']
# In een echte app zou dit in een database staan.
# Voor demo: gebruikersnaam -> password hash
ROLES = {'admin': generate_password_hash('admin123')}

def laad_medewerkers():
    if not os.path.exists(MEDEWERKERS_FILE):
        return []
    with open(MEDEWERKERS_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # migreer indien oude lijst van namen
            if data and isinstance(data, list) and isinstance(data[0], str):
                data = [{
                    'naam': n,
                    'voorkeur_diensten': [],  # bv ['Dagdienst']
                    'beschikbaarheid': {},    # datum->bool of 'x'
                    'max_nachtdiensten_per_maand': 6
                } for n in data]
            return data
        except Exception:
            return []

def sla_medewerkers_op(medewerkers):
    with open(MEDEWERKERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(medewerkers, f, ensure_ascii=False, indent=2)

def _index_medewerkers(medewerkers):
    return {m['naam']: m for m in medewerkers}

def fairness_score(teller, naam):
    return sum(teller[naam].values())

def _mag_toegewezen(wordt_gekeken_naam, dienst, vorige_dag, rooster_so_far, max_consec_nacht=2):
    if not rooster_so_far:
        return True
    # vorige dag dict
    if vorige_dag:
        # Regel: geen Dagdienst direct na Nachtdienst voor dezelfde persoon
        if dienst == 'Dagdienst' and vorige_dag.get('Nachtdienst') == wordt_gekeken_naam:
            return False
        # Regel: max 2 nachtdiensten op rij
        if dienst == 'Nachtdienst':
            # tel achteruit
            consec = 0
            for dag in reversed(rooster_so_far):
                if dag.get('Nachtdienst') == wordt_gekeken_naam:
                    consec += 1
                else:
                    break
            if consec >= max_consec_nacht:
                return False
    return True

def genereer_fair_rooster(start_datum, medewerkers, diensten, maanden=3):
    if not medewerkers:
        return []
    # counters
    counts = {m['naam']: {d:0 for d in diensten} for m in medewerkers}
    nacht_limieten = {m['naam']: m.get('max_nachtdiensten_per_maand', 6) for m in medewerkers}
    week_limieten = {m['naam']: m.get('max_diensten_per_week', 7) for m in medewerkers}
    rooster = []
    dag = start_datum
    eind_datum = start_datum + timedelta(days=maanden*30)
    by_name = _index_medewerkers(medewerkers)
    week_counts = {}  # (naam, jaarweek) -> aantal diensten
    while dag < eind_datum:
        datum_str = dag.strftime('%Y-%m-%d')
        dag_rooster = {'datum': datum_str}
        vorige_dag = rooster[-1] if rooster else None
        beschikbaar_cache = {}
        for dienst in diensten:
            kandidaten = []
            for m in medewerkers:
                naam = m['naam']
                # beschikbaarheid (indien ingevuld: beschikbaarheid[datum]==True)
                beschikbaar = m.get('beschikbaarheid', {})
                if beschikbaar and beschikbaar.get(datum_str) is False:
                    continue
                # nachtdienst limiet check per maand
                if dienst == 'Nachtdienst' and counts[naam]['Nachtdienst'] >= nacht_limieten.get(naam, 6):
                    continue
                # voorkeur boost
                voorkeuren = set(m.get('voorkeur_diensten', []))
                voorkeur_score = 1.0
                if voorkeuren:
                    if dienst in voorkeuren:
                        voorkeur_score = 0.5  # lagere score = eerder gekozen
                    else:
                        voorkeur_score = 1.5
                total = fairness_score(counts, naam)
                dienst_count = counts[naam][dienst]
                # week limiet check
                isocal = dag.isocalendar()
                jaarweek = f"{isocal[0]}-{isocal[1]}"
                huidig_week_count = week_counts.get((naam, jaarweek), 0)
                if huidig_week_count >= week_limieten.get(naam, 7):
                    continue
                if not _mag_toegewezen(naam, dienst, vorige_dag, rooster):
                    continue
                kandidaten.append((naam, total, dienst_count, voorkeur_score, random.random()))
            if not kandidaten:
                dag_rooster[dienst] = '-'
                continue
            # sorteer op: totaal minder diensten, minder van deze dienst, voorkeur_score, random stable
            kandidaten.sort(key=lambda x: (x[1], x[2], x[3], x[4]))
            gekozen_naam = kandidaten[0][0]
            dag_rooster[dienst] = gekozen_naam
            counts[gekozen_naam][dienst] += 1
            week_counts[(gekozen_naam, jaarweek)] = week_counts.get((gekozen_naam, jaarweek), 0) + 1
        rooster.append(dag_rooster)
        dag += timedelta(days=1)
    return rooster

def genereer_rooster(start_datum, medewerkers, diensten, maanden=3, fair=True):
    if fair:
        return genereer_fair_rooster(start_datum, medewerkers, diensten, maanden)
    # fallback eenvoudig
    names = [m['naam'] for m in medewerkers]
    rooster = []
    dag = start_datum
    eind_datum = start_datum + timedelta(days=maanden*30)
    while dag < eind_datum:
        dag_rooster = {'datum': dag.strftime('%Y-%m-%d')}
        if names:
            random.shuffle(names)
            for i, dienst in enumerate(diensten):
                dag_rooster[dienst] = names[i % len(names)]
        else:
            for dienst in diensten:
                dag_rooster[dienst] = '-'
        rooster.append(dag_rooster)
        dag += timedelta(days=1)
    return rooster


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            flash('Login vereist', 'warning')
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper

# Startpagina
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not session.get('user'):
            flash('Eerst inloggen om rooster te genereren.', 'error')
            return redirect(url_for('login'))
        start_datum = datetime.today()
        medewerkers = laad_medewerkers()
        rooster = genereer_rooster(start_datum, medewerkers, DIENSTEN, fair=True)
        session['rooster'] = rooster
        flash('Nieuw rooster gegenereerd', 'success')
        return redirect(url_for('rooster'))
    return render_template('index.html', user=session.get('user'))


# Rooster bekijken
@app.route('/rooster')
def rooster():
    rooster = session.get('rooster', None)
    return render_template('rooster.html', rooster=rooster, diensten=DIENSTEN, user=session.get('user'))

@app.route('/api/rooster')
def rooster_api():
    return jsonify(session.get('rooster', []))

@app.route('/export/rooster.json')
@login_required
def export_rooster_json():
    data = session.get('rooster', [])
    return jsonify(data)

# Medewerkersbeheer
@app.route('/medewerkers', methods=['GET', 'POST'])
@login_required
def medewerkers():
    medewerkers = laad_medewerkers()
    if request.method == 'POST':
        naam = request.form.get('naam', '').strip()
        if naam and not any(m['naam'] == naam for m in medewerkers):
            medewerkers.append({
                'naam': naam,
                'voorkeur_diensten': request.form.getlist('voorkeur_diensten'),
                'beschikbaarheid': {},
                'max_nachtdiensten_per_maand': int(request.form.get('max_nacht', 6)),
                'max_diensten_per_week': int(request.form.get('max_week', 7))
            })
            sla_medewerkers_op(medewerkers)
        return redirect(url_for('medewerkers'))
    return render_template('medewerkers.html', medewerkers=medewerkers, diensten=DIENSTEN)

# Medewerker verwijderen
@app.route('/verwijder_medewerker/<naam>', methods=['POST'])
@login_required
def verwijder_medewerker(naam):
    medewerkers = laad_medewerkers()
    nieuwe = [m for m in medewerkers if m['naam'] != naam]
    if len(nieuwe) != len(medewerkers):
        sla_medewerkers_op(nieuwe)
    return redirect(url_for('medewerkers'))

# Bewerken medewerker voorkeuren
@app.route('/medewerker/<naam>', methods=['GET','POST'])
@login_required
def edit_medewerker(naam):
    medewerkers = laad_medewerkers()
    for m in medewerkers:
        if m['naam'] == naam:
            if request.method == 'POST':
                m['voorkeur_diensten'] = request.form.getlist('voorkeur_diensten')
                m['max_nachtdiensten_per_maand'] = int(request.form.get('max_nacht', m.get('max_nachtdiensten_per_maand',6)))
                m['max_diensten_per_week'] = int(request.form.get('max_week', m.get('max_diensten_per_week',7)))
                # beschikbaarheid per datum (comma separated YYYY-MM-DD=1/0)
                raw = request.form.get('beschikbaarheid_raw','').strip()
                if raw:
                    beschikbaarheid = {}
                    for part in raw.split(','):
                        if '=' in part:
                            d,v = part.split('=',1)
                            d = d.strip()
                            if len(d)==10:
                                beschikbaarheid[d] = v.strip() in ('1','true','True','ja','yes')
                    m['beschikbaarheid'] = beschikbaarheid
                sla_medewerkers_op(medewerkers)
                return redirect(url_for('medewerkers'))
            return render_template('medewerker_edit.html', medewerker=m, diensten=DIENSTEN)
    return redirect(url_for('medewerkers'))

# CSV export
@app.route('/export/rooster.csv')
@login_required
def export_csv():
    rooster = session.get('rooster', [])
    if not rooster:
        return Response('Geen rooster', mimetype='text/plain')
    header = ['Datum'] + DIENSTEN
    lines = [','.join(header)]
    for r in rooster:
        lines.append(','.join([r['datum']] + [r.get(d,'') for d in DIENSTEN]))
    csv_data = '\n'.join(lines)
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=rooster.csv'})

# PDF export
@app.route('/export/rooster.pdf')
@login_required
def export_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    rooster = session.get('rooster', [])
    width, height = A4
    y = height - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, 'Dienstrooster')
    y -= 30
    c.setFont('Helvetica', 8)
    col_widths = [70] + [ (width-100)/len(DIENSTEN) for _ in DIENSTEN]
    c.drawString(40, y, 'Datum')
    x = 110
    for d in DIENSTEN:
        c.drawString(x, y, d)
        x += col_widths[1]
    y -= 12
    for dag in rooster:
        if y < 50:
            c.showPage(); y = height - 50; c.setFont('Helvetica', 8)
        c.drawString(40, y, dag['datum'])
        x = 110
        for d in DIENSTEN:
            c.drawString(x, y, dag.get(d,'-'))
            x += col_widths[1]
        y -= 10
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='rooster.pdf', mimetype='application/pdf')

# Auth
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username'); pw = request.form.get('password')
        stored = ROLES.get(user)
        if stored and check_password_hash(stored, pw):
            session['user'] = user
            flash('Ingelogd als %s' % user, 'success')
            return redirect(url_for('index'))
        flash('Ongeldige login', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Uitgelogd', 'info')
    return redirect(url_for('index'))

@app.route('/toggle_dark')
def toggle_dark():
    session['dark'] = not session.get('dark')
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)
