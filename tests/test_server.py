import copy
import http.cookiejar
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from exaclim import server

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.base = f'http://127.0.0.1:{cls.httpd.server_port}'
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def setUp(self):
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, path, data=None, client=None):
        request = urllib.request.Request(self.base+path, data=None if data is None else json.dumps(data).encode(),
                                         headers={'Content-Type':'application/json'})
        with (client or self.client).open(request) as r:
            return json.load(r)

    def test_emergency_cannot_be_cleared_by_ack_or_forged_payload(self):
        self.assertEqual(self.request('/api/emergency', {})['level'], 'emergency')
        self.assertEqual(self.request('/api/acknowledge', {})['level'], 'emergency')
        payload = dict(server.DEFAULT, emergency=False, emergency_latched=False, previous_level='green')
        self.assertEqual(self.request('/api/evaluate', payload)['level'], 'emergency')
        self.assertEqual(self.request('/api/worker')['level'], 'emergency')
        self.assertEqual(self.request('/api/reset', {})['level'], 'green')

    def test_client_can_raise_emergency_but_never_clear_it(self):
        result = self.request('/api/evaluate', dict(server.DEFAULT, emergency=True))
        self.assertEqual(result['level'], 'emergency')
        result = self.request('/api/evaluate', dict(server.DEFAULT, emergency=False))
        self.assertEqual(result['level'], 'emergency')

    def test_optional_forecast_is_computed_and_cannot_lower_floor(self):
        result = self.request('/api/evaluate', dict(server.DEFAULT, use_forecast=True))
        self.assertEqual(result['forecast']['status'], 'available')
        self.assertEqual(len(result['forecast']['rows']), 6)
        self.assertIn(result['level'], ['amber', 'red'])
        hot = dict(server.DEFAULT, temperature_c=40, workload='heavy', use_forecast=True)
        self.assertEqual(self.request('/api/evaluate', hot)['level'], 'red')

    def test_cookie_sessions_are_isolated(self):
        self.request('/api/emergency', {})
        stranger = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.assertEqual(self.request('/api/worker', client=stranger)['level'], 'green')
        self.assertEqual(self.request('/api/worker')['level'], 'emergency')

    def test_crew_suppression_and_no_worker_history(self):
        before = self.request('/api/crew?size=8')
        self.request('/api/emergency', {})
        self.assertEqual(self.request('/api/crew?size=8'), before)
        small = self.request('/api/crew?size=4')
        self.assertTrue(small['suppressed'])
        self.assertIsNone(small['counts'])
        self.assertNotIn('workers', before)

    def test_old_readings_become_cautious_without_manual_age_input(self):
        self.request('/api/evaluate', server.DEFAULT)
        with server.LOCK:
            for state in server.SESSIONS.values():
                if state['result']['level'] == 'green':
                    state['sample_at'] -= 121
        result = self.request('/api/worker')
        self.assertNotEqual(result['level'], 'green')

    def test_invalid_measurement_does_not_reassure(self):
        self.assertNotEqual(self.request('/api/evaluate', {'temperature_c':'invalid'})['level'], 'green')

    def test_malformed_body_and_cross_origin_are_rejected(self):
        for body, headers, expected in [
            (b'[]', {'Content-Type':'application/json'}, 400),
            (b'{"temperature_c":NaN}', {'Content-Type':'application/json'}, 400),
            (b'{}', {'Content-Type':'text/plain'}, 415),
            (b'{}', {'Content-Type':'application/json', 'Origin':'https://unrelated.example'}, 403)]:
            request = urllib.request.Request(self.base+'/api/evaluate', data=body, headers=headers)
            with self.assertRaises(urllib.error.HTTPError) as caught:
                self.client.open(request)
            self.assertEqual(caught.exception.code, expected)

    def test_static_assets_and_health(self):
        for path in ['/', '/app.js', '/styles.css']:
            with self.client.open(self.base+path) as r:
                self.assertEqual(r.status, 200)
                self.assertGreater(len(r.read()), 20)
        for asset in (server.ROOT / 'assets').glob('*.js'):
            with self.client.open(self.base+'/assets/'+asset.name) as response:
                self.assertEqual(response.status, 200)
        with self.assertRaises(urllib.error.HTTPError):
            self.client.open(self.base+'/assets/../app.js')
        self.assertEqual(self.request('/api/health')['status'], 'ok')
        with self.assertRaises(urllib.error.HTTPError):
            self.client.open(self.base+'/../exaclim/server.py')

    def test_forecast_fixture_labeled(self):
        result = self.request('/api/forecast')
        self.assertEqual(result['status'], 'synthetic')
        self.assertIsNone(result['fetched_at'])
        self.assertEqual(len(result['hourly']), 12)
