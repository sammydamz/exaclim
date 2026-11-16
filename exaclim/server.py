"""Local synthetic-data demonstrator. Not a production clinical service."""
import argparse
import copy
import http.cookies
import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .engine import evaluate
from . import forecast

ROOT = Path(__file__).resolve().parent.parent / 'dist'
LOCK = threading.RLock()
SESSIONS = {}
DEFAULT = dict(temperature_c=27, humidity_pct=55, workload='light', acclimatized=True,
               clothing='ordinary', duration_minutes=0, sensor_age_seconds=0)
ALLOWED = set(DEFAULT)
TTL_SECONDS = 8 * 3600


def crew(size):
    # Public synthetic fixture, never derived from private badge sessions.
    if size < 5:
        return {'suppressed': True, 'crew_size': None, 'counts': None,
                'source': 'Synthetic fixture', 'recommendation': 'Crew details suppressed below five consenting workers.'}
    red = size // 4
    amber = size // 3
    return {'suppressed': False, 'crew_size': size,
            'counts': {'green': size-red-amber, 'amber': amber, 'red': red, 'emergency': 0},
            'forecast': forecast.fixture()['hourly'], 'source': 'Synthetic fixture; not derived from worker sessions',
            'recommendation': 'Scenario planning: move heavy tasks away from 11:00–15:00; prepare shaded recovery and task rotation. Timings are illustrative, not approved work/rest limits.'}


class Handler(BaseHTTPRequestHandler):
    server_version = 'ExaclimDemo/0.1'

    def log_message(self, fmt, *args):
        # Avoid logging request payloads, cookies or individual exposure values.
        pass

    def json_response(self, data, status=200, cookie=None):
        body = json.dumps(data, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        if cookie:
            self.send_header('Set-Cookie', f'exaclim_session={cookie}; HttpOnly; SameSite=Strict; Path=/')
        self.end_headers()
        self.wfile.write(body)

    def session(self):
        jar = http.cookies.SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie', ''))
        except http.cookies.CookieError:
            pass
        token = jar['exaclim_session'].value if 'exaclim_session' in jar else None
        now = time.monotonic()
        for old in list(SESSIONS):
            if now - SESSIONS[old]['touched'] > TTL_SECONDS:
                del SESSIONS[old]
        if token not in SESSIONS:
            token = secrets.token_urlsafe(32)
            SESSIONS[token] = {'payload': copy.deepcopy(DEFAULT), 'result': evaluate(DEFAULT),
                               'sample_at': now, 'touched': now}
        state = SESSIONS[token]
        state['touched'] = now
        return token, state

    def refresh(self, state):
        payload = dict(state['payload'])
        age = payload.get('sensor_age_seconds', 0)
        if type(age) in (int, float):
            payload['sensor_age_seconds'] = age + time.monotonic()-state['sample_at']
        payload['previous_level'] = state['result']['level']
        payload['emergency_latched'] = state['result']['emergency_latched']
        payload['acknowledge'] = state['result'].get('acknowledged', False)
        state['result'] = evaluate(payload)
        return state['result']

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == '/api/health':
            return self.json_response({'status': 'ok', 'mode': 'synthetic-data demo'})
        if parsed.path == '/api/crew':
            try:
                size = int(parse_qs(parsed.query).get('size', ['8'])[0])
                if not 0 <= size <= 100:
                    raise ValueError()
            except ValueError:
                return self.json_response({'error': 'size must be an integer from 0 to 100'}, 400)
            return self.json_response(crew(size))
        if parsed.path == '/api/forecast':
            if parse_qs(parsed.query).get('mode') == ['live']:
                try:
                    return self.json_response(forecast.live())
                except Exception:
                    data = forecast.fixture()
                    data.update(status='synthetic-fallback', error='Live forecast unavailable; showing labeled synthetic scenario.')
                    return self.json_response(data)
            return self.json_response(forecast.fixture())
        if parsed.path == '/api/worker':
            with LOCK:
                token, state = self.session()
                return self.json_response(self.refresh(state), cookie=token)
        paths = {'/': 'index.html', '/app.js': 'app.js', '/styles.css': 'styles.css'}
        if parsed.path in paths:
            path = ROOT / paths[parsed.path]
        elif parsed.path.startswith('/assets/'):
            path = (ROOT / parsed.path.lstrip('/')).resolve()
            if path.parent != (ROOT / 'assets').resolve() or path.suffix not in ('.js', '.css'):
                return self.json_response({'error': 'Not found'}, 404)
        else:
            return self.json_response({'error': 'Not found'}, 404)
        if not path.is_file():
            return self.json_response({'error': 'Web assets unavailable'}, 503)
        body = path.read_bytes()
        self.send_response(200)
        types = {'.html':'text/html', '.js':'text/javascript', '.css':'text/css'}
        self.send_header('Content-Type', types[path.suffix]+'; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        # UI SDK injects part layout styles; scripts remain restricted to local bundles.
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # The UI is same-origin; reject browser cross-site form requests too.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.json_response({'error': 'Cross-origin request rejected'}, 403)
        route = urlsplit(self.path).path
        if route not in ('/api/evaluate', '/api/acknowledge', '/api/emergency', '/api/reset'):
            return self.json_response({'error': 'Not found'}, 404)
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.json_response({'error': 'Use application/json'}, 415)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16384:
                raise ValueError()
            data = json.loads(self.rfile.read(size), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            if not isinstance(data, dict):
                raise ValueError()
        except (ValueError, json.JSONDecodeError):
            return self.json_response({'error': 'Invalid JSON object or body size'}, 400)
        with LOCK:
            token, state = self.session()
            previous = self.refresh(state)
            if route == '/api/reset':
                state['payload'] = copy.deepcopy(DEFAULT)
                state['sample_at'] = time.monotonic()
                state['result'] = evaluate(DEFAULT)
            elif route == '/api/acknowledge':
                state['result']['acknowledged'] = True
            elif route == '/api/emergency':
                payload = dict(state['payload'], emergency=True, emergency_latched=True)
                state['result'] = evaluate(payload)
            else:
                # Client cannot clear trusted emergency state or assert a safe previous level.
                payload = {k: data.get(k) for k in ALLOWED}
                if data.get('use_forecast') is True:
                    payload['forecast'] = [dict(temperature_c=row['temperature_c'], humidity_pct=row['humidity_pct'],
                                                minutes_ahead=(i+1)*60, time=row['hour'])
                                           for i, row in enumerate(forecast.fixture()['hourly'][1:7])]
                payload.update(previous_level=previous['level'], emergency_latched=previous['emergency_latched'],
                               emergency=data.get('emergency') is True)
                state['result'] = evaluate(payload)
                state['payload'] = {k: value for k, value in payload.items() if k not in ('previous_level', 'emergency_latched')}
                state['sample_at'] = time.monotonic()
            return self.json_response(state['result'], cookie=token)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Exaclim synthetic demo listening on loopback port {args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
