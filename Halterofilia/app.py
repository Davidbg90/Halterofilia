import os
from flask import Flask, render_template, request, jsonify
from parser import parse_plan
from pdf_extractor import extract_text_from_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB máx


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.get_json(force=True)

    maxes = {
        'snatch':      _to_float(data.get('snatch')),
        'clean_jerk':  _to_float(data.get('clean_jerk')),
        'jerk':        _to_float(data.get('jerk')),
        'back_squat':  _to_float(data.get('back_squat')),
        'front_squat': _to_float(data.get('front_squat')),
    }
    # Jerk sin 1RM → usa C&J
    if maxes['jerk'] is None and maxes['clean_jerk'] is not None:
        maxes['jerk'] = maxes['clean_jerk']

    # Sentadilla trasera sin 1RM → convención halterofilia: 120% del C&J
    bs_auto = False
    if maxes['back_squat'] is None and maxes['clean_jerk'] is not None:
        maxes['back_squat'] = round(maxes['clean_jerk'] * 1.2 * 2) / 2
        bs_auto = True

    plan_text = data.get('plan', '')
    days = parse_plan(plan_text, maxes)
    return jsonify({
        'days': days,
        'bs_auto': bs_auto,
        'bs_base': maxes.get('back_squat'),
    })


@app.route('/subir-pdf', methods=['POST'])
def subir_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No se recibió ningún fichero'}), 400
    file = request.files['pdf']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'El fichero debe ser un PDF'}), 400
    try:
        text = extract_text_from_pdf(file.read())
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Error al leer el PDF: {e}'}), 500


def _to_float(value) -> float | None:
    try:
        v = float(str(value).replace(',', '.'))
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
