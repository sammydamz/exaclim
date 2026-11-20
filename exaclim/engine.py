"""Transparent, deliberately illustrative scenario engine (no clinical validity).

No output establishes WBGT, body temperature, a safe work duration or diagnosis.
Callers must retain emergency_latched state and authorize resolution separately.
"""
from math import isfinite

LEVELS = ('green', 'amber', 'red', 'emergency')
STALE_SECONDS = 120
AMBER_SCORE = 40
RED_SCORE = 70
ACTIONS = {
    'green': 'Continue the site heat-control plan; maintain access to water and rest. Green does not establish safety.',
    'amber': 'Pause for a shaded cooling break, check conditions and reduce work intensity under the site plan.',
    'red': 'Stop the affected task, move to a cooler safe area and notify the designated supervisor.',
    'emergency': 'Activate the site emergency procedure and obtain urgent help. Do not leave the person alone.',
}


def _number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    # Compare bounds before float conversion: JSON integers can exceed float range.
    if not low <= value <= high or not isfinite(value):
        return None
    return float(value)


def _score(t, h, workload, clothing, acclimatized, duration):
    parts = {
        'temperature': max(0, (t - 25) * 4),
        'humidity': max(0, h - 40) * .3,
        'workload': {'light': 0, 'moderate': 10, 'heavy': 20}[workload],
        'clothing': 12 if clothing == 'protective' else 0,
        'acclimatization': 0 if acclimatized else 8,
        'duration': duration / 12,
    }
    score = round(min(100, sum(parts.values())), 2)
    return score, parts


def _level(score):
    return 'red' if score >= RED_SCORE else 'amber' if score >= AMBER_SCORE else 'green'


def evaluate(payload):
    """Evaluate one synthetic worker scenario and optional forecast.

    Inputs: temperature_c [-10,60], humidity_pct [0,100], workload
    light/moderate/heavy, clothing ordinary/protective, acclimatized bool,
    duration_minutes [0,960], sensor_age_seconds [0,604800]. Required inputs
    omitted or malformed force cautious mode. Forecast optional list of rows
    with temperature_c/humidity_pct, minutes_ahead [0,2880], optional time.
    No mutable state, network calls, personal identifiers or learned model.
    """
    if not isinstance(payload, dict):
        payload = {}
    reasons, invalid = [], []
    values = {}
    bounds = {'temperature_c': (-10, 60), 'humidity_pct': (0, 100),
              'duration_minutes': (0, 960), 'sensor_age_seconds': (0, 604800)}
    for name, (low, high) in bounds.items():
        values[name] = _number(payload.get(name), low, high)
        if values[name] is None:
            invalid.append(name)
    workload = payload.get('workload')
    clothing = payload.get('clothing')
    acclimatized = payload.get('acclimatized')
    if workload not in ('light', 'moderate', 'heavy'):
        invalid.append('workload')
    if clothing not in ('ordinary', 'protective'):
        invalid.append('clothing')
    if not isinstance(acclimatized, bool):
        invalid.append('acclimatized')
    for flag in ('emergency', 'emergency_latched', 'acknowledge'):
        if flag in payload and not isinstance(payload[flag], bool):
            invalid.append(flag)
    previous = payload.get('previous_level', 'green')
    if previous not in LEVELS:
        previous = 'amber'
        invalid.append('previous_level')
    stale = values['sensor_age_seconds'] is not None and values['sensor_age_seconds'] > STALE_SECONDS
    quality = 'invalid' if invalid else 'stale' if stale else 'fresh'
    score, components = None, {}
    baseline = 'amber'
    if not invalid:
        score, components = _score(values['temperature_c'], values['humidity_pct'], workload,
                                   clothing, acclimatized, values['duration_minutes'])
        baseline = _level(score)
        reasons.append('Illustrative index combines environment, declared task, clothing, acclimatization and elapsed exposure; it is not WBGT.')
    if invalid or stale:
        baseline = max((baseline, 'amber', previous), key=LEVELS.index)
        reasons.append('Cautious fallback: ' + ('invalid or missing inputs: ' + ', '.join(invalid) if invalid else 'zone data older than 120 seconds') + '. Verify conditions using the manual site plan.')
    forecast_rows, forecast_invalid = [], 0
    forecast_input = payload.get('forecast', [])
    if not isinstance(forecast_input, list):
        forecast_input, forecast_invalid = [], 1
    for row in forecast_input[:72]:
        if not isinstance(row, dict):
            forecast_invalid += 1
            continue
        t = _number(row.get('temperature_c'), -10, 60)
        h = _number(row.get('humidity_pct'), 0, 100)
        ahead = _number(row.get('minutes_ahead'), 0, 2880)
        if t is None or h is None or ahead is None or invalid:
            forecast_invalid += 1
            continue
        fs, _ = _score(t, h, workload, clothing, acclimatized,
                        min(960, values['duration_minutes'] + ahead))
        forecast_rows.append({'time': str(row.get('time', ''))[:80], 'minutes_ahead': ahead,
                              'score': fs, 'level': _level(fs)})
    forecast_rows.sort(key=lambda r: r['minutes_ahead'])
    forecast_worst = max((r['level'] for r in forecast_rows), key=LEVELS.index, default=baseline)
    # Escalation concerns the explicit forecast horizon, never a diagnosed event.
    level = max((baseline, forecast_worst), key=LEVELS.index)
    if LEVELS.index(forecast_worst) > LEVELS.index(baseline):
        reasons.append('Forecast scenario raises caution above the current baseline; review upcoming work and cooling arrangements.')
    if forecast_invalid:
        reasons.append('Invalid forecast rows ignored; current baseline remains in force.')
    emergency = (payload.get('emergency') is True or payload.get('emergency_latched') is True or previous == 'emergency')
    if emergency:
        level = 'emergency'
        reasons.append('Help or prior emergency overrides every score and forecast; acknowledgement does not resolve it.')
    return {
        'model_version': 'illustrative-v1', 'illustrative_only': True,
        'level': level, 'baseline_level': baseline, 'score': score,
        'components': components, 'reasons': reasons, 'action': ACTIONS[level],
        'data_quality': quality, 'invalid_fields': invalid, 'stale_after_seconds': STALE_SECONDS,
        'emergency_latched': emergency, 'acknowledged': payload.get('acknowledge') is True,
        'forecast': {'status': 'available' if forecast_rows else 'unavailable',
                     'rows': forecast_rows, 'invalid_rows': forecast_invalid,
                     'minutes_to_illustrative_red': next((r['minutes_ahead'] for r in forecast_rows if r['level'] == 'red'), None),
                     'interpretation': 'Scenario threshold crossing only; not time to heat illness or a safe work allowance.'},
        'limitations': 'Synthetic demonstration. Not validated for work/rest prescriptions, WBGT assessment, diagnosis or real-world protection.',
    }
