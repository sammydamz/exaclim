"""Forecast adapter. Fixture forecasts are never presented as observations."""
import datetime as dt
import json
import math
import urllib.request

URL = ('https://api.open-meteo.com/v1/forecast?latitude=5.6037&longitude=-0.1870'
       '&hourly=temperature_2m,relative_humidity_2m&forecast_days=2&timezone=Africa%2FAccra')
LIMITATION = 'Grid weather is not measured site microclimate or occupational WBGT. Not a personal heat-strain forecast.'

def fixture():
    temps = [27, 28, 30, 32, 34, 35, 34, 32, 30, 29, 28, 27]
    return {'source': 'Synthetic Accra construction scenario', 'status': 'synthetic',
            'fetched_at': None, 'limitation': LIMITATION,
            'hourly': [{'hour': f'{h+7:02}:00', 'temperature_c': t,
                        'humidity_pct': 76 - (t-27)*2} for h, t in enumerate(temps)]}

def live(opener=urllib.request.urlopen):
    """Fail visibly; caller can display a labeled fixture instead."""
    with opener(URL, timeout=8) as response:
        data = json.loads(response.read(1_000_000))
    hourly = data['hourly']
    times, temps, humidities = (hourly[k] for k in ('time', 'temperature_2m', 'relative_humidity_2m'))
    if not times or not len(times) == len(temps) == len(humidities):
        raise ValueError('Incomplete forecast response')
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for timestamp, temp, humidity in zip(times, temps, humidities):
        point = dt.datetime.fromisoformat(timestamp).replace(tzinfo=dt.timezone.utc)
        if point < now.replace(minute=0, second=0, microsecond=0):
            continue
        if (type(temp) not in (int, float) or type(humidity) not in (int, float)
                or not math.isfinite(temp) or not math.isfinite(humidity)
                or not -20 <= temp <= 65 or not 0 <= humidity <= 100):
            raise ValueError('Invalid forecast observation')
        rows.append({'hour': timestamp, 'temperature_c': temp, 'humidity_pct': humidity})
        if len(rows) == 24:
            break
    if not rows:
        raise ValueError('Forecast contains no current or future hours')
    return {'source': 'Open-Meteo numerical weather forecast', 'status': 'live',
            'fetched_at': now.isoformat(), 'hourly': rows, 'limitation': LIMITATION,
            'attribution': 'Weather data: Open-Meteo and its national weather service sources (CC BY 4.0)',
            'coordinates': {'latitude': 5.6037, 'longitude': -0.1870},
            'model_issue_time': 'Not supplied by this endpoint; fetched_at is retrieval time.'}
