"""Local authenticated synthetic supervisor demo; not a real-worker deployment."""
import argparse
import copy
import http.cookies
import json
import math
import os
import re
import secrets
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from . import dashboard
from .store import Store

ROOT = Path(__file__).resolve().parent.parent / 'dist'
COOKIE = 'exaclim_supervisor'
MAX_BODY = 16384


class APIError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def utcnow():
    return datetime.now(timezone.utc)


def iso(value):
    return value.isoformat().replace('+00:00', 'Z')


def public_dashboard(state, site_id, user):
    result = dashboard.snapshot(state, site_id)
    result['sites'] = [{k: site[k] for k in ('id', 'name', 'latitude', 'longitude', 'timezone')}
                       for key, site in state['sites'].items() if key in user['site_ids']]
    result['source'] = 'Synthetic watches, shared-phone gateway and weather scenario'
    result['mode'] = 'synthetic-demo'
    result['updated_at'] = result.get('generated_at', iso(utcnow()))
    forecast = result['forecast']
    forecast.setdefault('status', 'synthetic')
    forecast.setdefault('fetched_at', forecast.get('generated_at'))
    forecast.setdefault('stale', False)
    for day in forecast['days']:
        day['windows'] = day.get('windows', day.get('red_windows', []))
        for window in day['windows']:
            window.setdefault('level', 'red')
            window.setdefault('label', 'High-risk scenario window')
        for hour in day['hours']:
            hour.setdefault('time', hour.get('start'))
            hour.setdefault('hour', hour.get('local_time', hour.get('start', '')))
            hour.setdefault('level', 'amber' if forecast.get('stale') else hour.get('risk', 'amber'))
            hour.setdefault('quality', hour.get('data_quality', 'synthetic'))
    suggestions = {entry['group_id']: entry for entry in result.get('suggestions', [])}
    for group in result['groups']:
        group.setdefault('level', group.get('state', 'amber'))
        group.setdefault('total_workers', group.get('expected_contributors', 0))
        group.setdefault('valid_contributors', group.get('fresh_contributors', 0))
        group.setdefault('updated_at', group.get('last_sample_at'))
        group.setdefault('received_at', group.get('last_received_at'))
        group['suggestion'] = suggestions.get(group['id'])
        if group['counts'] is not None:
            group['counts']['unknown'] = group.get('unknown_contributors', 0)
    for event in result['emergencies']:
        event['acknowledged'] = bool(event.get('acknowledged_at'))
    return result


class Handler(BaseHTTPRequestHandler):
    server_version = 'ExaclimSupervisorDemo/1.0'

    def log_message(self, fmt, *args):
        pass

    def respond(self, value, status=200, token=None, clear_cookie=False):
        payload = json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'private, no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        secure = '; Secure' if self.server.secure_cookies else ''
        if token:
            self.send_header('Set-Cookie', f'{COOKIE}={token}; Path=/; HttpOnly; SameSite=Strict{secure}')
        if clear_cookie:
            self.send_header('Set-Cookie', f'{COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0{secure}')
        self.end_headers()
        self.wfile.write(payload)

    def token(self):
        jar = http.cookies.SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie', ''))
        except http.cookies.CookieError:
            return None
        return jar[COOKIE].value if COOKIE in jar else None

    def user(self, site_id=None):
        user = self.server.store.user_for_session(self.token())
        if not user:
            raise APIError(401, 'unauthenticated', 'Sign in to the synthetic supervisor demo.')
        if site_id and site_id not in user['site_ids']:
            raise APIError(403, 'site_forbidden', 'This supervisor cannot access the requested site.')
        return user

    def origin(self):
        origin = self.headers.get('Origin')
        host = self.headers.get('Host', '')
        if origin and origin not in ('http://' + host, 'https://' + host):
            raise APIError(403, 'cross_origin', 'Cross-origin changes are not permitted.')
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            raise APIError(403, 'cross_site', 'Cross-site changes are not permitted.')

    def body(self, allowed):
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise APIError(415, 'content_type', 'Use application/json.')
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                raise ValueError()
            data = json.loads(self.rfile.read(length), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, UnicodeError, json.JSONDecodeError):
            raise APIError(400, 'invalid_json', 'Provide a bounded JSON object with finite values.')
        if not isinstance(data, dict):
            raise APIError(400, 'invalid_json', 'Provide a JSON object.')
        if not set(data) <= set(allowed):
            raise APIError(422, 'unsupported_fields', 'Unsupported fields; personal watch profiles are not accepted.')
        return data

    def site(self, state, site_id):
        if site_id not in state['sites']:
            raise APIError(404, 'site_not_found', 'Site not found.')
        return state['sites'][site_id]

    def handle_error(self, operation):
        try:
            operation()
        except APIError as error:
            self.respond({'error': error.message, 'code': error.code, 'request_id': secrets.token_hex(6)}, error.status)
        except (ValueError, TypeError, KeyError) as error:
            self.respond({'error': str(error)[:180], 'code': 'validation', 'request_id': secrets.token_hex(6)}, 422)
        except Exception:
            self.respond({'error': 'The request could not be completed. Try again.',
                          'code': 'internal_error', 'request_id': secrets.token_hex(6)}, 500)

    def do_GET(self):
        self.handle_error(self.get)

    def get(self):
        path = urlsplit(self.path).path
        if path == '/api/health':
            return self.respond({'status': 'ok', 'mode': 'synthetic-demo', 'product': 'Exaclim'})
        if path == '/api/v1/auth/me':
            return self.respond({'user': self.user(), 'mode': 'synthetic-demo'})
        match = re.fullmatch(r'/api/v1/sites/([^/]+)/(dashboard|setup)', path)
        if match:
            site_id, operation = match.groups()
            user = self.user(site_id)
            state = self.server.store.load()
            site = self.site(state, site_id)
            if operation == 'dashboard':
                return self.respond(public_dashboard(state, site_id, user))
            return self.respond({'site': {k: site[k] for k in ('id', 'name', 'latitude', 'longitude', 'timezone')},
                                 'crews': [{k: crew[k] for k in ('id', 'name', 'count')} for crew in site['crews']],
                                 'assignments': site['assignments'], 'mode': 'synthetic-demo'})
        if path.startswith('/api/'):
            raise APIError(404, 'not_found', 'Endpoint not found.')
        files = {'/': ROOT/'index.html', '/app.js': ROOT/'app.js', '/styles.css': ROOT/'styles.css',
                 '/exaclim.png': ROOT/'exaclim.png'}
        if path in files:
            file = files[path]
        elif path.startswith('/assets/'):
            file = (ROOT/path.lstrip('/')).resolve()
            if file.parent != (ROOT/'assets').resolve() or file.suffix not in ('.js', '.css', '.woff2', '.woff'):
                raise APIError(404, 'not_found', 'Asset not found.')
        else:
            raise APIError(404, 'not_found', 'Page not found.')
        if not file.is_file():
            raise APIError(503, 'build_missing', 'Frontend build unavailable. Run npm run build.')
        body = file.read_bytes()
        mime = {'.html':'text/html', '.js':'text/javascript', '.css':'text/css',
                '.woff2':'font/woff2', '.woff':'font/woff', '.png':'image/png'}[file.suffix]
        self.send_response(200)
        self.send_header('Content-Type', mime + ('; charset=utf-8' if file.suffix in ('.html','.js','.css') else ''))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        # SDK part layout requires runtime styles; scripts and fonts remain local.
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        self.handle_error(self.post)

    def post(self):
        self.origin()
        path = urlsplit(self.path).path
        if path == '/api/v1/auth/login':
            data = self.body(('email', 'password'))
            email, password = data.get('email'), data.get('password')
            if not isinstance(email, str) or not isinstance(password, str) or len(email)>320 or len(password)>1024:
                raise APIError(422, 'credentials', 'Provide the synthetic demo email and password.')
            key = self.client_address[0]
            recent = [stamp for stamp in self.server.failed_logins.get(key, []) if time.monotonic()-stamp < 60]
            if len(recent) >= 10:
                raise APIError(429, 'rate_limited', 'Too many attempts. Wait a minute and try again.')
            token = self.server.store.authenticate(email, password)
            if not token:
                self.server.failed_logins[key] = recent + [time.monotonic()]
                raise APIError(401, 'invalid_credentials', 'Email or password does not match the demo account.')
            self.server.failed_logins.pop(key, None)
            return self.respond({'user': self.server.store.user_for_session(token), 'mode': 'synthetic-demo'}, token=token)
        if path == '/api/v1/auth/logout':
            self.body(())
            self.server.store.logout(self.token())
            return self.respond({'ok': True}, clear_cookie=True)
        match = re.fullmatch(r'/api/v1/sites/([^/]+)/(crews|assignments|simulate)', path)
        if match:
            site_id, operation = match.groups()
            user = self.user(site_id)
            self.site(self.server.store.load(), site_id)
            if operation == 'crews':
                data = self.body(('name', 'count'))
                result = self.server.store.update(lambda state: dashboard.add_crew(state, site_id, data.get('name'), data.get('count')))
                return self.respond({'crew': result, **result}, 201)
            if operation == 'assignments':
                data = self.body(('crew_id', 'worker_name', 'watch_id'))
                result = self.server.store.update(lambda state: dashboard.assign_watch(state, site_id, data.get('crew_id'), data.get('worker_name'), data.get('watch_id')))
                return self.respond({'assignment': result, **result}, 201)
            data = self.body(('scenario',))
            scenario = data.get('scenario')
            if not isinstance(scenario, str):
                raise APIError(422, 'scenario', 'Choose a named synthetic scenario.')
            self.server.store.update(lambda state: dashboard.scenario(state, site_id, scenario))
            return self.respond({'ok': True, 'scenario': scenario,
                                 'dashboard': public_dashboard(self.server.store.load(), site_id, user)})
        match = re.fullmatch(r'/api/v1/emergencies/([^/]+)/ack', path)
        if match:
            user = self.user()
            self.body(())
            event_id = match.group(1)
            state = self.server.store.load()
            site_id = next((key for key, site in state['sites'].items()
                            if any(event['id'] == event_id for event in site['events'])), None)
            if site_id is None:
                raise APIError(404, 'event_not_found', 'Help event not found.')
            self.user(site_id)
            event = self.server.store.update(lambda state: dashboard.acknowledge(state, event_id, user['name']))
            return self.respond({'ok': True, 'id': event['id'], 'acknowledged': True,
                                 'acknowledged_at': event['acknowledged_at'], 'acknowledged_by': event['acknowledged_by'],
                                 'watch_state_cleared': False})
        raise APIError(404, 'not_found', 'Endpoint not found.')

    def do_PATCH(self):
        self.handle_error(self.patch)

    def patch(self):
        self.origin()
        match = re.fullmatch(r'/api/v1/sites/([^/]+)', urlsplit(self.path).path)
        if not match:
            raise APIError(404, 'not_found', 'Endpoint not found.')
        site_id = match.group(1)
        self.user(site_id)
        data = self.body(('name', 'latitude', 'longitude', 'timezone'))
        state = self.server.store.load()
        current = self.site(state, site_id)
        changed = {key: data.get(key, current[key]) for key in ('name', 'latitude', 'longitude', 'timezone')}
        if not isinstance(changed['name'], str) or not changed['name'].strip() or len(changed['name']) > 100:
            raise ValueError('Site name must contain 1–100 characters.')
        for key, low, high in [('latitude', -90, 90), ('longitude', -180, 180)]:
            value = changed[key]
            if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
                raise ValueError('Coordinates must be finite and in range.')
        try:
            ZoneInfo(changed['timezone'])
        except (ZoneInfoNotFoundError, TypeError, ValueError):
            raise ValueError('Use a valid IANA timezone, such as Africa/Accra.')
        changed['name'] = changed['name'].strip()
        def update(state):
            site = self.site(state, site_id)
            site.update(changed)
            return {key: site[key] for key in ('id', 'name', 'latitude', 'longitude', 'timezone')}
        return self.respond({'site': self.server.store.update(update), 'ok': True})


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def server_close(self):
        super().server_close()
        self.store.close()


def make_server(host='127.0.0.1', port=0, db_path=':memory:', *, secure_cookies=False):
    if os.environ.get('EXACLIM_MODE', 'demo') != 'demo':
        raise RuntimeError('This build only supports synthetic demo mode, not real-worker deployment.')
    server = DemoServer((host, port), Handler)
    server.store = Store(db_path, dashboard.initial_state)
    server.secure_cookies = secure_cookies
    server.failed_logins = {}
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--db', default=str(Path(__file__).resolve().parents[1]/'.local/exaclim-demo.sqlite3'))
    args = parser.parse_args()
    server = make_server(args.host, args.port, args.db)
    print(f'Exaclim synthetic supervisor demo listening on {args.host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
