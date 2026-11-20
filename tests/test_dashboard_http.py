"""Independent HTTP acceptance checks for the synthetic Dashboard V1.

Uses real HTTP, cookie handling and temporary SQLite files. These tests validate
software contracts only: they do not qualify watch hardware or clinical policy.
"""
import concurrent.futures
import http.cookiejar
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from exaclim import server


class DashboardHTTPTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='exaclim-v1-test-')
        self.db_path = str(Path(self.directory.name) / 'dashboard.sqlite3')
        self._start()
        self.jar = http.cookiejar.CookieJar()
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def _start(self):
        self.httpd = server.make_server(host='127.0.0.1', port=0, db_path=self.db_path)
        self.base = f'http://127.0.0.1:{self.httpd.server_port}'
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def _stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        if hasattr(self.httpd.store, 'close'):
            self.httpd.store.close()

    def tearDown(self):
        self._stop()
        self.directory.cleanup()

    def request(self, path, body=None, *, method=None, origin=None, client=None, raw=None,
                content_type='application/json'):
        headers = {'Accept': 'application/json'}
        data = raw
        if body is not None:
            data = json.dumps(body, allow_nan=False).encode()
        if data is not None:
            headers['Content-Type'] = content_type
            headers['Origin'] = self.base if origin is None else origin
        request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            response = (client or self.client).open(request, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            payload = response.read()
            return response.status, json.loads(payload) if payload else None, response.headers

    def login(self):
        status, body, headers = self.request('/api/v1/auth/login', {
            'email': 'demo@exaclim.test', 'password': 'Exaclim2026!'})
        self.assertEqual(status, 200, body)
        return body, headers

    def dashboard(self, site='accra'):
        status, body, _ = self.request(f'/api/v1/sites/{site}/dashboard')
        self.assertEqual(status, 200, body)
        return body

    def simulate(self, scenario):
        status, body, _ = self.request('/api/v1/sites/accra/simulate', {'scenario': scenario})
        self.assertEqual(status, 200, body)
        return self.dashboard()

    def test_health_is_public_but_session_identity_is_not(self):
        self.assertEqual(self.request('/api/health')[0], 200)
        self.assertEqual(self.request('/api/v1/auth/me')[0], 401)

    def test_all_site_read_surfaces_require_login(self):
        for path in ['/api/v1/sites/accra/dashboard', '/api/v1/sites/accra/setup']:
            with self.subTest(path=path):
                status, body, _ = self.request(path)
                self.assertEqual(status, 401, body)

    def test_invalid_login_never_issues_authenticated_session(self):
        status, body, _ = self.request('/api/v1/auth/login', {
            'email': 'demo@exaclim.test', 'password': 'wrong-password'})
        self.assertEqual(status, 401, body)
        self.assertEqual(self.request('/api/v1/auth/me')[0], 401)

    def test_login_cookie_has_browser_protections(self):
        _, headers = self.login()
        cookie = headers.get('Set-Cookie', '')
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite=Strict', cookie)
        self.assertIn('Path=/', cookie)
        self.assertEqual(self.request('/api/v1/auth/me')[0], 200)

    def test_logout_revokes_cookie_and_protected_access(self):
        self.login()
        self.assertEqual(self.request('/api/v1/auth/logout', {})[0], 200)
        self.assertEqual(self.request('/api/v1/auth/me')[0], 401)
        self.assertEqual(self.request('/api/v1/sites/accra/dashboard')[0], 401)

    def test_forecast_has_two_accra_local_days_and_hour_quality(self):
        self.login()
        snapshot = self.dashboard()
        self.assertEqual(snapshot['site']['timezone'], 'Africa/Accra')
        days = snapshot['forecast']['days']
        self.assertEqual(len(days), 2)
        self.assertNotEqual(days[0]['date'], days[1]['date'])
        for day in days:
            self.assertEqual(len(day['hours']), 24)
            self.assertEqual(len({hour['time'] for hour in day['hours']}), 24)
            for hour in day['hours']:
                self.assertIn(hour['level'], ('green', 'amber', 'red', 'unknown'))
                self.assertTrue(hour['quality'])
                self.assertTrue(hour['label'])

    def test_snapshot_labels_synthetic_provenance_and_is_not_cacheable(self):
        self.login()
        status, snapshot, headers = self.request('/api/v1/sites/accra/dashboard')
        self.assertEqual(status, 200)
        self.assertIn('synthetic', json.dumps({'source': snapshot['source'], 'mode': snapshot['mode']}).lower())
        self.assertIn('no-store', headers.get('Cache-Control', ''))

    def test_small_crews_are_combined_without_overlap(self):
        self.login()
        groups = self.dashboard()['groups']
        self.assertTrue(any(len(group['crew_ids']) > 1 for group in groups))
        ids = [crew_id for group in groups for crew_id in group['crew_ids']]
        self.assertEqual(len(ids), len(set(ids)), 'Overlapping crew totals enable subtraction')
        for group in groups:
            if not group['suppressed']:
                self.assertGreaterEqual(group['valid_contributors'], 3)
                self.assertGreaterEqual(group['total_workers'], 3)
                self.assertEqual(sum(group['counts'].values()), group['total_workers'])

    def test_normal_snapshot_does_not_expose_individual_routine_health(self):
        self.login()
        snapshot = self.dashboard()
        forbidden = {'worker_name', 'individual_score', 'clothing', 'acclimatization',
                     'acclimatized', 'body_temperature', 'symptoms', 'worker_history'}
        def inspect(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value), forbidden.intersection(value))
                for child in value.values(): inspect(child)
            elif isinstance(value, list):
                for child in value: inspect(child)
        inspect({key: value for key, value in snapshot.items() if key != 'emergencies'})

    def test_unknown_site_is_not_accessible(self):
        self.login()
        status, _, _ = self.request('/api/v1/sites/other-company/dashboard')
        self.assertIn(status, (403, 404))

    def test_existing_out_of_scope_site_and_emergency_are_forbidden(self):
        self.login()
        def add_restricted_site(state):
            from exaclim.dashboard import scenario
            import copy
            restricted = copy.deepcopy(state['sites']['accra'])
            restricted['id'] = 'restricted-site'
            restricted['events'] = []
            state['sites']['restricted-site'] = restricted
            scenario(state, 'restricted-site', 'help')
            return restricted['events'][0]['id']
        event_id = self.httpd.store.update(add_restricted_site)
        for operation in ('dashboard', 'setup'):
            self.assertEqual(self.request(f'/api/v1/sites/restricted-site/{operation}')[0], 403)
        self.assertEqual(self.request(f'/api/v1/emergencies/{event_id}/ack', {})[0], 403)
        self.assertEqual(self.request('/api/v1/sites/restricted-site/simulate', {'scenario': 'normal'})[0], 403)

    def test_forged_cookie_never_grants_access(self):
        request = urllib.request.Request(self.base + '/api/v1/sites/accra/dashboard',
            headers={'Cookie': 'exaclim_supervisor=forged-session-token'})
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request, timeout=10)
        self.assertEqual(caught.exception.code, 401)

    def test_connection_loss_cannot_leave_reassuring_green_or_numeric_private_breakdown(self):
        self.login()
        snapshot = self.simulate('connection-lost')
        self.assertTrue(snapshot['groups'])
        for group in snapshot['groups']:
            self.assertNotEqual(group['level'], 'green')
            self.assertTrue(group['data_quality'])
            if group['valid_contributors'] < 3:
                self.assertTrue(group['suppressed'])
                self.assertIsNone(group['counts'])

    def test_reconnection_restores_only_explicit_new_synthetic_readings(self):
        self.login()
        self.simulate('connection-lost')
        snapshot = self.simulate('reconnect')
        self.assertTrue(any(group['valid_contributors'] >= 3 and not group['suppressed']
                            for group in snapshot['groups']))

    def test_help_has_named_exception_and_ack_does_not_resolve_group(self):
        self.login()
        snapshot = self.simulate('help')
        events = [event for event in snapshot['emergencies'] if not event['acknowledged']]
        self.assertTrue(events)
        event = events[0]
        self.assertTrue(event['worker_name'])
        self.assertTrue(event['crew_name'])
        self.assertTrue(event['occurred_at'])
        self.assertFalse({'score', 'clothing', 'symptoms'}.intersection(event))
        status, receipt, _ = self.request(f"/api/v1/emergencies/{event['id']}/ack", {})
        self.assertEqual(status, 200, receipt)
        after = self.dashboard()
        self.assertFalse(any(item['id'] == event['id'] and not item['acknowledged']
                             for item in after['emergencies']))
        help_groups = [group for group in after['groups'] if group['help_active']]
        self.assertTrue(help_groups, 'ACK must not resolve the independent help state')
        self.assertTrue(all(group['level'] in ('red', 'emergency') for group in help_groups))

    def test_repeated_acknowledgement_returns_same_canonical_receipt(self):
        self.login()
        event = self.simulate('help')['emergencies'][0]
        path = f"/api/v1/emergencies/{event['id']}/ack"
        first = self.request(path, {})
        second = self.request(path, {})
        self.assertEqual(first[0], 200)
        self.assertEqual(second[0], 200)
        self.assertEqual(first[1], second[1])

    def test_concurrent_acknowledgements_preserve_one_receipt_and_other_event(self):
        self.login()
        first = self.simulate('help')['emergencies'][0]
        events = self.simulate('delayed-help')['emergencies']
        other_id = next(e['id'] for e in events if e['id'] != first['id'])
        cookie = '; '.join(f'{c.name}={c.value}' for c in self.jar)
        def acknowledge(_):
            request = urllib.request.Request(self.base + f"/api/v1/emergencies/{first['id']}/ack",
                data=b'{}', headers={'Content-Type': 'application/json', 'Origin': self.base,
                                     'Cookie': cookie})
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.load(response)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            receipts = list(pool.map(acknowledge, range(4)))
        self.assertTrue(all(receipt == receipts[0] for receipt in receipts))
        self.assertTrue(any(e['id'] == other_id and not e['acknowledged']
                            for e in self.dashboard()['emergencies']))

    def test_delayed_help_is_labeled_and_cannot_replace_existing_event(self):
        self.login()
        first = self.simulate('help')['emergencies'][0]['id']
        events = self.simulate('delayed-help')['emergencies']
        self.assertIn(first, {event['id'] for event in events})
        self.assertTrue(any(event['delayed'] for event in events))
        self.assertGreaterEqual(len(events), 2)

    def test_emergency_mutation_requires_auth_and_same_origin(self):
        self.login()
        event = self.simulate('help')['emergencies'][0]
        path = f"/api/v1/emergencies/{event['id']}/ack"
        self.assertEqual(self.request(path, {}, origin='https://evil.example')[0], 403)
        stranger = urllib.request.build_opener()
        self.assertEqual(self.request(path, {}, client=stranger)[0], 401)
        self.assertTrue(any(not e['acknowledged'] for e in self.dashboard()['emergencies']))

    def test_acknowledgement_survives_backend_restart(self):
        self.login()
        first = self.simulate('help')['emergencies'][0]
        events = self.simulate('delayed-help')['emergencies']
        other_id = next(e['id'] for e in events if e['id'] != first['id'])
        self.assertEqual(self.request(f"/api/v1/emergencies/{first['id']}/ack", {})[0], 200)
        self._stop()
        self._start()
        # Login afresh: session durability is not assumed; emergency durability is.
        self.login()
        after = self.dashboard()['emergencies']
        self.assertFalse(any(e['id'] == first['id'] and not e['acknowledged'] for e in after))
        self.assertTrue(any(e['id'] == other_id and not e['acknowledged'] for e in after))
        self.assertTrue(any(g['help_active'] for g in self.dashboard()['groups']))

    def test_site_setup_is_separate_and_persists_saved_location(self):
        self.login()
        status, setup, _ = self.request('/api/v1/sites/accra/setup')
        self.assertEqual(status, 200)
        self.assertIn('crews', setup)
        self.assertIn('assignments', setup)
        status, body, _ = self.request('/api/v1/sites/accra', {
            'name': 'Accra synthetic QA site', 'latitude': 5.6037,
            'longitude': -0.187, 'timezone': 'Africa/Accra'}, method='PATCH')
        self.assertEqual(status, 200, body)
        self.assertEqual(self.dashboard()['site']['name'], 'Accra synthetic QA site')

    def test_invalid_site_coordinates_and_timezone_are_rejected(self):
        self.login()
        for patch in [{'latitude': 200}, {'longitude': -190}, {'timezone': 'Not/AZone'}]:
            with self.subTest(patch=patch):
                status, _, _ = self.request('/api/v1/sites/accra', patch, method='PATCH')
                self.assertIn(status, (400, 422))

    def test_create_small_crew_does_not_publish_single_person_risk(self):
        self.login()
        status, body, _ = self.request('/api/v1/sites/accra/crews', {'name': 'QA synthetic crew', 'count': 1})
        self.assertEqual(status, 201, body)
        snapshot = self.dashboard()
        for group in snapshot['groups']:
            if not group['suppressed']:
                self.assertGreaterEqual(group['valid_contributors'], 3)
        self.assertNotIn('QA Worker Private', json.dumps(snapshot))

    def test_cloud_rejects_private_issuance_profiles(self):
        self.login()
        status, setup, _ = self.request('/api/v1/sites/accra/setup')
        self.assertEqual(status, 200)
        crew_id = setup['crews'][0]['id']
        for private in [{'clothing': 'restrictive'}, {'acclimatization': 'new'},
                        {'individual_score': 22}, {'worker_history': []}]:
            payload = {'crew_id': crew_id, 'worker_name': 'QA Synthetic Worker',
                       'watch_id': 'QA-PRIVATE-REJECT', **private}
            with self.subTest(field=next(iter(private))):
                status, _, _ = self.request('/api/v1/sites/accra/assignments', payload)
                self.assertIn(status, (400, 422))

    def test_assignment_save_is_unique_and_not_joined_to_routine_risk(self):
        self.login()
        status, crew, _ = self.request('/api/v1/sites/accra/crews',
            {'name': 'Synthetic issuance QA', 'count': 3})
        self.assertEqual(status, 201)
        assignment = {'crew_id': crew['id'], 'worker_name': 'QA Synthetic Issuance Worker',
                      'watch_id': 'QA-UNIQUE-WATCH'}
        status, _, _ = self.request('/api/v1/sites/accra/assignments', assignment)
        self.assertEqual(status, 201)
        self.assertEqual(self.request('/api/v1/sites/accra/assignments', assignment)[0], 422)
        _, setup, _ = self.request('/api/v1/sites/accra/setup')
        saved = [a for a in setup['assignments'] if a['watch_id'] == assignment['watch_id']]
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]['worker_name'], assignment['worker_name'])
        snapshot = self.dashboard()
        self.assertNotIn(assignment['worker_name'], json.dumps(snapshot))
        self.assertNotIn(assignment['watch_id'], json.dumps(snapshot))

    def test_malformed_json_never_causes_internal_server_error(self):
        self.login()
        for raw in [b'{', b'[]', b'null', b'{"count":NaN}', b'{"count":Infinity}']:
            with self.subTest(raw=raw):
                status, body, _ = self.request('/api/v1/sites/accra/crews', raw=raw)
                self.assertEqual(status, 400, body)
        self.assertEqual(self.request('/api/health')[0], 200)

    def test_oversized_request_is_rejected_without_mutating_state(self):
        self.login()
        _, before, _ = self.request('/api/v1/sites/accra/setup')
        status, _, _ = self.request('/api/v1/sites/accra/crews',
            raw=json.dumps({'name': 'x' * 20000, 'count': 3}).encode())
        self.assertEqual(status, 400)
        _, after, _ = self.request('/api/v1/sites/accra/setup')
        self.assertEqual(before['crews'], after['crews'])

    def test_cross_origin_and_non_json_forms_cannot_create_crew(self):
        self.login()
        path = '/api/v1/sites/accra/crews'
        self.assertEqual(self.request(path, {'name': 'Invalid', 'count': 3},
                                      origin='https://evil.example')[0], 403)
        self.assertEqual(self.request(path, raw=b'name=Invalid&count=3',
                                      content_type='application/x-www-form-urlencoded')[0], 415)

    def test_out_of_scope_worker_views_and_traversal_are_not_served(self):
        self.login()
        for path in ['/api/worker', '/api/crew', '/api/evaluate', '/api/v1/workers',
                     '/api/v1/sites/accra/workers', '/../exaclim/server.py']:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)

    def test_invalid_scenario_cannot_reset_existing_help(self):
        self.login()
        event_id = self.simulate('help')['emergencies'][0]['id']
        status, _, _ = self.request('/api/v1/sites/accra/simulate', {'scenario': 'erase-everything'})
        self.assertIn(status, (400, 422))
        self.assertIn(event_id, {e['id'] for e in self.dashboard()['emergencies']})


if __name__ == '__main__':
    unittest.main(verbosity=2)
