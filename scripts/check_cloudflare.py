#!/usr/bin/env python3
"""Exercise a running synthetic Worker through HTTP; no Cloudflare account required."""
import argparse
import concurrent.futures
import http.cookiejar
import json
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8787')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

    def request(path, data=None, method=None, status=200, headers=None):
        req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(),
                                     method=method, headers={'Content-Type': 'application/json', 'User-Agent': 'Exaclim-Demo-QA/1.0', **(headers or {})})
        try:
            response = opener.open(req, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            assert response.status == status, (path, response.status, response.read().decode())
            return json.load(response)

    prefix = '/api/v1/sites/accra'
    assert request('/api/health')['mode'] == 'synthetic-demo'
    request(prefix + '/dashboard', status=401)
    request('/api/v1/auth/login', {'email': 'demo@exaclim.test', 'password': 'wrong'}, status=401)
    account = request('/api/v1/auth/login', {'email': 'demo@exaclim.test', 'password': 'Exaclim2026!'})
    assert account['user']['site_ids'] == ['accra', 'tema']
    request('/api/v1/sites/forbidden/dashboard', status=403)
    request('/api/session', status=404)
    request(prefix + '/simulate', {'scenario': 'normal'}, headers={'Origin': 'https://other.invalid'}, status=403)
    request(prefix + '/simulate', {'scenario': 'normal', 'clothing': 'private'}, status=422)
    request(prefix + '/simulate', {'scenario': 'normal'})
    dashboard = request(prefix + '/dashboard')
    assert all(g['expected_contributors'] >= 3 for g in dashboard['groups'])
    assert all(g['counts'] is None or 'unknown' in g['counts'] for g in dashboard['groups'])
    assert 'worker_name' not in json.dumps(dashboard['groups'])
    assert len(dashboard['forecast']['days']) == 2
    setup = request(prefix + '/setup')
    assert setup['assignments']
    request(prefix, {'name': setup['site']['name']}, method='PATCH')
    request(prefix + '/simulate', {'scenario': 'help'})
    incident = request(prefix + '/dashboard')['emergencies'][-1]
    ack_path = '/api/v1/emergencies/' + incident['id'] + '/ack'
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        acknowledgements = list(pool.map(lambda _: request(ack_path, {}), range(4)))
    assert len({a['acknowledged_at'] for a in acknowledgements}) == 1
    assert all(a['acknowledged_by'] == 'Demo supervisor' and not a['watch_state_cleared'] for a in acknowledgements)
    dashboard = request(prefix + '/dashboard')
    assert incident['id'] not in [e['id'] for e in dashboard['emergencies']]
    assert any(g['help_active'] and g['state'] == 'red' for g in dashboard['groups'])
    request(prefix + '/simulate', {'scenario': 'resolve-help'})
    request(prefix + '/simulate', {'scenario': 'connection-lost'})
    before = {e['id'] for e in request(prefix + '/dashboard')['emergencies']}
    request(prefix + '/simulate', {'scenario': 'help'})
    assert {e['id'] for e in request(prefix + '/dashboard')['emergencies']} == before
    request(prefix + '/simulate', {'scenario': 'reconnect'})
    delivered = [e for e in request(prefix + '/dashboard')['emergencies'] if e['id'] not in before]
    assert len(delivered) == 1 and delivered[0]['delayed'] and delivered[0]['received_at']
    request('/api/v1/emergencies/' + delivered[0]['id'] + '/ack', {})
    request(prefix + '/simulate', {'scenario': 'resolve-help'})
    request(prefix + '/simulate', {'scenario': 'normal'})
    request('/api/v1/auth/logout', {})
    request('/api/v1/auth/me', status=401)
    print('PASS: Worker authentication, scope, privacy, forecast, setup, concurrent acknowledgement, offline delivery and logout')


if __name__ == '__main__':
    main()
