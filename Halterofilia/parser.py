import re
from calculator import lift_key_for, calc_weight, youtube_search_url

_SEMANA = re.compile(r'^SEMANA\b', re.IGNORECASE)
_DIA    = re.compile(r'^D[IÍ]A\s+(\d+)\b', re.IGNORECASE)
_EX_HDR = re.compile(r'^([A-Z])\)\s+(.+)', re.IGNORECASE)
_NOTAS  = re.compile(r'^NOTAS\s*:', re.IGNORECASE)

# Serie con porcentaje: "1x2 75%"  |  "5x4 80-90%"  |  "4x1 80%+"
_SERIES = re.compile(
    r'^(\d+)\s*[xX×]\s*(\d+(?:[-–]\d+)?)'
    r'\s+(\d+(?:[.,]\d+)?(?:[-–]\d+(?:[.,]\d+)?)?)'
    r'\s*%\+?'
)
# Serie sin porcentaje al inicio de línea: "5 x 5" o "5 x 5 (descripción...)"
_SERIES_NO_PCT = re.compile(r'^(\d+)\s*[xX×]\s*(\d+(?:[-–]\d+)?)(?:\s|$)')

# Series inline al final del nombre: "Back squat 5x4 75-80%"  /  "Split jerk 5x5"
_INLINE = re.compile(
    r'^(.*?)\s+'
    r'(\d+)\s*[xX×]\s*(\d+(?:[-–]\d+)?)'
    r'(?:\s+(\d+(?:[.,]\d+)?(?:[-–]\d+(?:[.,]\d+)?)?)\s*%\+?)?'
    r'\s*$',
    re.IGNORECASE,
)


def _parse_pct(s: str | None) -> tuple[float | None, float | None]:
    if not s:
        return None, None
    s = s.replace(',', '.').replace('–', '-')
    if '-' in s:
        lo, hi = s.split('-', 1)
        return float(lo), float(hi)
    return float(s), None


def parse_plan(text: str, maxes: dict) -> list[dict]:
    days: list[dict] = []
    current_day: dict | None = None
    current_ex:  dict | None = None
    in_notes = False

    def close_exercise():
        nonlocal current_ex
        if current_ex is not None and current_day is not None:
            current_day['exercises'].append(current_ex)
        current_ex = None

    def close_day():
        nonlocal current_day
        close_exercise()
        if current_day is not None:
            days.append(current_day)
        current_day = None

    def new_series(sets, reps, pct_str) -> dict:
        lo, hi = _parse_pct(pct_str)
        key = current_ex['lift_key']
        return {
            'sets':      sets,
            'reps':      reps,
            'pct_lo':    lo,
            'pct_hi':    hi,
            'weight':    calc_weight(maxes, key, lo) if lo else None,
            'weight_hi': calc_weight(maxes, key, hi) if hi else None,
        }

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('*'):
            continue

        if _SEMANA.match(line):
            continue

        # ── Cabecera de día — siempre tiene prioridad ──────────────────────
        m = _DIA.match(line)
        if m:
            close_day()
            current_day = {'day': f'Día {m.group(1)}', 'exercises': []}
            in_notes = False
            continue

        # ── Cabecera de ejercicio — rompe notas en curso ───────────────────
        m = _EX_HDR.match(line)
        if m:
            close_exercise()
            in_notes = False
            letter = m.group(1).upper()
            rest   = m.group(2).strip()

            mi = _INLINE.match(rest)
            if mi and mi.group(2):
                name    = mi.group(1).strip() or rest
                sets    = int(mi.group(2))
                reps    = mi.group(3)
                pct_str = mi.group(4)
            else:
                name    = rest
                sets    = None
                reps    = None
                pct_str = None

            if current_day is None:
                current_day = {'day': 'Semana', 'exercises': []}

            current_ex = {
                'letter':      letter,
                'name':        name,
                'lift_key':    lift_key_for(name),
                'series':      [],
                'notes':       '',
                'youtube_url': youtube_search_url(name),
            }

            if sets is not None:
                current_ex['series'].append(new_series(sets, reps, pct_str))
            continue

        # ── NOTAS ──────────────────────────────────────────────────────────
        if _NOTAS.match(line):
            in_notes = True
            body = line[line.index(':') + 1:].strip()
            if current_ex is not None:
                current_ex['notes'] = body
            continue

        # ── Continuación de notas ──────────────────────────────────────────
        if in_notes:
            if current_ex is not None:
                current_ex['notes'] = (current_ex.get('notes', '') + ' ' + line).strip()
            continue

        # ── Serie con porcentaje ───────────────────────────────────────────
        m = _SERIES.match(line)
        if m and current_ex is not None:
            current_ex['series'].append(new_series(int(m.group(1)), m.group(2), m.group(3)))
            continue

        # ── Serie sin porcentaje ───────────────────────────────────────────
        m = _SERIES_NO_PCT.match(line)
        if m and current_ex is not None:
            current_ex['series'].append(new_series(int(m.group(1)), m.group(2), None))
            continue

    close_day()
    return days
