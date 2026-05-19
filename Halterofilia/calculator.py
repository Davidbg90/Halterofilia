import urllib.parse

LIFT_GROUPS = {
    'snatch': [
        'snatch', 'hang snatch', 'power snatch', 'hang power snatch',
        'slow pull hang power snatch', 'snatch pull', 'snatch deadlift',
        'block snatch', 'snatch balance', 'overhead squat', 'ohs',
        'muscle snatch', 'hang muscle snatch', 'drop snatch',
    ],
    'clean_jerk': [
        'clean and jerk', 'clean & jerk', 'clean jerk',
        'hang clean', 'power clean', 'clean pull', 'clean deadlift',
        'deficit clean deadlift', 'block clean', 'clean',
    ],
    'jerk': [
        'jerk drives', 'split jerk', 'push jerk', 'power jerk', 'jerk balance', 'jerk',
    ],
    'back_squat':  ['back squat', 'squat'],
    'front_squat': ['front squat'],
}

# Más largo primero para evitar que "jerk" capte antes que "split jerk", etc.
_ALIAS_MAP: dict[str, str] = {}
for _key, _names in LIFT_GROUPS.items():
    for _n in _names:
        _ALIAS_MAP[_n] = _key


def lift_key_for(name: str) -> str | None:
    normalized = name.lower().strip()
    if normalized in _ALIAS_MAP:
        return _ALIAS_MAP[normalized]
    # Busca la alias MÁS LARGA que sea subcadena (evita "jerk" antes que "split jerk")
    best = None
    best_len = 0
    for alias, key in _ALIAS_MAP.items():
        if alias in normalized and len(alias) > best_len:
            best, best_len = key, len(alias)
    return best


def calc_weight(maxes: dict, lift_key: str | None, pct: float | None) -> float | None:
    if not lift_key or pct is None:
        return None
    base = maxes.get(lift_key)
    if base is None:
        return None
    return round(base * pct / 100 * 2) / 2   # redondeo a 0.5 kg


def youtube_search_url(exercise_name: str) -> str:
    query = f"weightlifting {exercise_name} technique"
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
