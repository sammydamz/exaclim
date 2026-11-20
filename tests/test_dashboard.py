import json
import unittest
from datetime import datetime, timedelta, timezone

from exaclim.dashboard import initial_state, snapshot, add_site, add_crew, assign_watch, scenario, acknowledge

NOW = datetime(2026, 11, 19, 10, 0, tzinfo=timezone.utc)


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.state = initial_state(NOW)

    def _empty_site(self):
        return add_site(self.state, 'Test site', 5, 0, 'Africa/Accra')['id']

    def _populated_crew(self, site, count, name):
        crew = add_crew(self.state, site, name, count)
        for i in range(count):
            assign_watch(self.state, site, crew['id'], f'Synthetic {name} {i}', f'{name}-{i}')
        return crew

    def test_initial_groups_nonoverlapping_two_plus_one(self):
        result = snapshot(self.state, now=NOW)
        self.assertEqual(sorted(g['total_workers'] for g in result['groups']), [3, 5])
        ids = [c for g in result['groups'] for c in g['crew_ids']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(g['counts'] is not None for g in result['groups']))
        self.assertEqual(sum(sum(g['counts'].values()) for g in result['groups']), 8)

    def test_two_plus_four_combines_whole_crew(self):
        site = self._empty_site()
        a = self._populated_crew(site, 2, 'A')
        b = self._populated_crew(site, 4, 'B')
        scenario(self.state, site, 'normal', NOW)
        groups = snapshot(self.state, site, NOW)['groups']
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['total_workers'], 6)
        self.assertEqual(set(groups[0]['crew_ids']), {a['id'], b['id']})

    def test_small_entire_site_and_low_valid_contributors_suppress(self):
        site = self._empty_site()
        self._populated_crew(site, 2, 'Small')
        scenario(self.state, site, 'normal', NOW)
        for sample in self.state['sites'][site]['samples'].values():
            sample['level'] = 'green'
        group = snapshot(self.state, site, NOW)['groups'][0]
        self.assertIsNone(group['counts'])
        self.assertIsNone(group['budget'])
        self.assertEqual(group['state'], 'amber')  # insufficient privacy must not reassure
        accra = self.state['sites']['accra']
        for watch in accra['crews'][0]['watch_ids'][2:]:
            del accra['samples'][watch]
        group = next(g for g in snapshot(self.state, now=NOW)['groups'] if g['total_workers'] == 5)
        self.assertTrue(group['suppressed'])
        self.assertIsNone(group['counts'])
        self.assertIsNone(group['budget'])
        self.assertEqual(group['fresh_contributors'], 2)

    def test_120_second_boundary_stale_preserves_red(self):
        scenario(self.state, 'accra', 'rising-heat', NOW)
        at_boundary = snapshot(self.state, now=NOW + timedelta(seconds=120))
        self.assertTrue(all(g['unknown_contributors'] == 0 for g in at_boundary['groups']))
        aged = snapshot(self.state, now=NOW + timedelta(seconds=120.01))
        self.assertTrue(all(g['unknown_contributors'] > 0 for g in aged['groups']))
        self.assertTrue(all(g['state'] == 'red' for g in aged['groups']))
        self.assertTrue(all(g['counts'] is None for g in aged['groups']))

    def test_future_sample_does_not_stay_fresh(self):
        sample = next(iter(self.state['sites']['accra']['samples'].values()))
        sample['sampled_at'] = '2099-01-01T00:00:00Z'
        groups = snapshot(self.state, now=NOW)['groups']
        self.assertEqual(sum(g['unknown_contributors'] for g in groups), 1)
        self.assertTrue(any(g['state'] in ('amber', 'red') for g in groups))

    def test_named_event_ack_is_separate_from_help_resolution(self):
        first = scenario(self.state, 'accra', 'help', NOW)['emergencies'][0]
        self.assertEqual(first['worker_name'], 'Ama Mensah')
        event = acknowledge(self.state, first['id'], 'Supervisor One', NOW + timedelta(seconds=1))
        repeat = acknowledge(self.state, first['id'], 'Supervisor Two', NOW + timedelta(seconds=2))
        self.assertEqual(event['acknowledged_at'], repeat['acknowledged_at'])
        self.assertEqual(repeat['acknowledged_by'], 'Supervisor One')
        result = snapshot(self.state, now=NOW + timedelta(seconds=2))
        self.assertEqual(result['emergencies'], [])
        self.assertEqual(result['active_help_count'], 1)
        group = next(g for g in result['groups'] if first['crew_id'] in g['crew_ids'])
        self.assertEqual(group['state'], 'red')
        self.assertTrue(group['help_active'])
        scenario(self.state, 'accra', 'connection-lost', NOW + timedelta(seconds=3))
        self.assertTrue(any(g['help_active'] and g['state'] == 'red' for g in snapshot(self.state, now=NOW + timedelta(seconds=3))['groups']))
        result = scenario(self.state, 'accra', 'resolve-help', NOW + timedelta(seconds=4))
        self.assertEqual(result['active_help_count'], 0)

    def test_resolution_before_ack_keeps_named_banner(self):
        event = scenario(self.state, 'accra', 'help', NOW)['emergencies'][0]
        result = scenario(self.state, 'accra', 'resolve-help', NOW + timedelta(seconds=1))
        self.assertEqual(result['active_help_count'], 0)
        self.assertEqual(len(result['emergencies']), 1)
        self.assertEqual(result['emergencies'][0]['id'], event['id'])
        self.assertIsNotNone(result['emergencies'][0]['resolved_at'])
        acknowledge(self.state, event['id'], now=NOW + timedelta(seconds=2))
        self.assertEqual(snapshot(self.state, now=NOW + timedelta(seconds=2))['emergencies'], [])

    def test_forecast_stale_after_six_hours_and_get_does_not_refresh(self):
        boundary = snapshot(self.state, now=NOW + timedelta(hours=6))['forecast']
        self.assertFalse(boundary['stale'])
        later = NOW + timedelta(hours=6, seconds=1)
        stale = snapshot(self.state, now=later)['forecast']
        self.assertTrue(stale['stale'])
        self.assertEqual(stale['days'][0]['hours'][0]['display_risk'], 'unknown')
        self.assertEqual(self.state['sites']['accra']['forecast_generated_at'], '2026-11-19T10:00:00Z')
        refreshed = scenario(self.state, 'accra', 'reconnect', later)['forecast']
        self.assertFalse(refreshed['stale'])
        self.assertEqual(refreshed['age_seconds'], 0)

    def test_delayed_events_order_and_ack_one_only(self):
        scenario(self.state, 'accra', 'help', NOW)
        result = scenario(self.state, 'accra', 'delayed-help', NOW + timedelta(seconds=10))
        self.assertEqual(len(result['emergencies']), 2)
        self.assertTrue(result['emergencies'][0]['delayed'])
        acknowledge(self.state, result['emergencies'][0]['id'], now=NOW + timedelta(seconds=11))
        self.assertEqual(len(snapshot(self.state, now=NOW + timedelta(seconds=11))['emergencies']), 1)

    def test_offline_help_outbox_survives_json_and_delivers_once(self):
        scenario(self.state, 'accra', 'connection-lost', NOW)
        occurred = NOW + timedelta(seconds=10)
        result = scenario(self.state, 'accra', 'help', occurred)
        self.assertEqual(result['emergencies'], [])
        self.assertEqual(result['active_help_count'], 0)
        serialized = json.dumps(result)
        self.assertNotIn('Ama Mensah', serialized)
        self.assertNotIn('pending_events', serialized)
        self.assertFalse(any(g['help_active'] for g in result['groups']))
        queued = self.state['sites']['accra']['pending_events'][0]
        self.assertIsNone(queued['received_at'])
        original_id = queued['id']
        restored = json.loads(json.dumps(self.state))
        self.assertEqual(snapshot(restored, now=occurred)['emergencies'], [])
        received = NOW + timedelta(minutes=5)
        result = scenario(restored, 'accra', 'reconnect', received)
        self.assertEqual(len(result['emergencies']), 1)
        event = result['emergencies'][0]
        self.assertEqual(event['id'], original_id)
        self.assertEqual(event['occurred_at'], occurred.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(event['received_at'], received.isoformat().replace('+00:00', 'Z'))
        self.assertTrue(event['delayed'])
        self.assertEqual(restored['sites']['accra']['pending_events'], [])
        scenario(restored, 'accra', 'reconnect', received + timedelta(seconds=1))
        self.assertEqual(len(restored['sites']['accra']['events']), 1)
        scenario(restored, 'accra', 'normal', received + timedelta(seconds=2))
        self.assertEqual(len(restored['sites']['accra']['events']), 1)
        self.assertEqual(snapshot(restored, now=received + timedelta(seconds=2))['active_help_count'], 1)

    def test_normal_resumes_synthetic_gateway_without_clearing_events(self):
        scenario(self.state, 'accra', 'help', NOW)
        scenario(self.state, 'accra', 'connection-lost', NOW + timedelta(seconds=1))
        scenario(self.state, 'accra', 'symptom', NOW + timedelta(seconds=2))
        self.assertEqual(len(self.state['sites']['accra']['pending_events']), 1)
        result = scenario(self.state, 'accra', 'normal', NOW + timedelta(seconds=3))
        self.assertEqual(len(result['emergencies']), 2)
        self.assertEqual(result['active_help_count'], 2)
        self.assertTrue(self.state['sites']['accra']['gateway_connected'])

    def test_forecast_two_local_days_and_half_open_window(self):
        forecast = snapshot(self.state, now=NOW)['forecast']
        self.assertEqual([d['date'] for d in forecast['days']], ['2026-11-19', '2026-11-20'])
        self.assertEqual([len(d['hours']) for d in forecast['days']], [24, 24])
        for day in forecast['days']:
            window = day['red_windows'][0]
            self.assertTrue(window['start_local'].startswith(day['date'] + 'T11:00'))
            self.assertTrue(window['end_local'].startswith(day['date'] + 'T15:00'))
            red = [h for h in day['hours'] if h['risk'] == 'red']
            self.assertEqual(len(red), 4)
            self.assertEqual(red[-1]['end'], window['end'])
        self.assertEqual(forecast['source_type'], 'synthetic')
        self.assertIsNone(forecast['provider_issue_time'])

    def test_dst_coverage_and_site_timezone_not_browser(self):
        site = add_site(self.state, 'New York test', 40, -74, 'America/New_York')['id']
        # UTC Nov 1 03:00 is still Oct 31 in New York; next day repeats an hour.
        result = snapshot(self.state, site, datetime(2026, 11, 1, 3, tzinfo=timezone.utc))
        self.assertEqual(result['forecast']['days'][0]['date'], '2026-10-31')
        self.assertEqual([len(d['hours']) for d in result['forecast']['days']], [24, 25])
        labels = [h['label'] for h in result['forecast']['days'][1]['hours']]
        self.assertIn('01:00 -0400', labels)
        self.assertIn('01:00 -0500', labels)

    def test_no_routine_individual_values_or_identity_in_snapshot(self):
        result = snapshot(self.state, now=NOW)
        serialized = json.dumps(result)
        self.assertNotIn('Ama Mensah', serialized)
        self.assertNotIn('DEMO-001', serialized)
        self.assertNotIn('assignments', result)
        self.assertNotIn('admin', result)
        self.assertNotIn('clothing', serialized)
        self.assertNotIn('acclimatized', serialized)
        self.assertFalse(any('budget' in s for s in self.state['sites']['accra']['samples'].values()))

    def test_validation_and_duplicate_watch_ids(self):
        site = self._empty_site()
        crew = add_crew(self.state, site, 'New crew', 3)
        for count in (0, 21, True, '3'):
            with self.assertRaises(ValueError):
                add_crew(self.state, site, 'Invalid', count)
        with self.assertRaises(ValueError):
            assign_watch(self.state, site, crew['id'], 'Name', 'demo-001')
        with self.assertRaises(ValueError):
            add_crew(self.state, site, 'new CREW', 3)
        with self.assertRaises(ValueError):
            add_site(self.state, 'Bad', 10**400, 0, 'Africa/Accra')
        with self.assertRaises(ValueError):
            add_site(self.state, 'Bad', 0, 0, 'Not/AZone')
        with self.assertRaises(ValueError):
            scenario(self.state, 'accra', 'not-supported', NOW)
        with self.assertRaises(ValueError):
            acknowledge(self.state, 'missing', now=NOW)
        with self.assertRaises(ValueError):
            snapshot(self.state, now=datetime(2026, 11, 19))

    def test_state_json_roundtrip_and_empty_site(self):
        restored = json.loads(json.dumps(self.state))
        self.assertEqual(snapshot(self.state, now=NOW), snapshot(restored, now=NOW))
        empty = snapshot(restored, 'tema', NOW)
        self.assertEqual(empty['groups'], [])
        self.assertEqual(empty['suggestions'], [])
        self.assertEqual(empty['emergencies'], [])


if __name__ == '__main__':
    unittest.main()
