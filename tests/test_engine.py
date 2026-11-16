import math
import unittest
from exaclim.engine import evaluate

BASE = dict(temperature_c=26, humidity_pct=45, workload='light', clothing='ordinary',
            acclimatized=True, duration_minutes=10, sensor_age_seconds=0)


class EngineTests(unittest.TestCase):
    def test_low_scenario_is_explainable(self):
        r = evaluate(BASE)
        self.assertEqual(r['level'], 'green')
        self.assertAlmostEqual(r['score'], 6.33)
        self.assertTrue(r['illustrative_only'])

    def test_work_and_ppe_increase_index(self):
        a = evaluate(BASE)
        b = evaluate({**BASE, 'workload': 'heavy', 'clothing': 'protective', 'acclimatized': False})
        self.assertGreater(b['score'], a['score'])
        self.assertEqual(b['level'], 'amber')

    def test_hot_case_red(self):
        self.assertEqual(evaluate({**BASE, 'temperature_c': 40, 'humidity_pct': 80})['level'], 'red')

    def test_stale_not_green_and_preserves_red(self):
        self.assertEqual(evaluate({**BASE, 'sensor_age_seconds': 121})['level'], 'amber')
        self.assertEqual(evaluate({**BASE, 'sensor_age_seconds': 121, 'previous_level': 'red'})['level'], 'red')
        self.assertEqual(evaluate({**BASE, 'sensor_age_seconds': 120})['data_quality'], 'fresh')
        self.assertEqual(evaluate({**BASE, 'sensor_age_seconds': 120.01})['data_quality'], 'stale')
        self.assertEqual(evaluate({**BASE, 'sensor_age_seconds': 120.01})['level'], 'amber')

    def test_exact_score_boundaries(self):
        scenario = {**BASE, 'humidity_pct': 40, 'duration_minutes': 0}
        for temperature, expected_score, expected_level in [
                (34.99, 39.96, 'green'), (35, 40, 'amber'),
                (42.49, 69.96, 'amber'), (42.5, 70, 'red')]:
            with self.subTest(temperature=temperature):
                result = evaluate({**scenario, 'temperature_c': temperature})
                self.assertEqual(result['score'], expected_score)
                self.assertEqual(result['level'], expected_level)

    def test_huge_json_integer_rejected_without_overflow(self):
        huge = 10 ** 400
        for field in ('temperature_c', 'humidity_pct', 'duration_minutes', 'sensor_age_seconds'):
            with self.subTest(field=field):
                result = evaluate({**BASE, field: huge})
                self.assertEqual(result['data_quality'], 'invalid')
                self.assertEqual(result['level'], 'amber')
        result = evaluate({**BASE, 'forecast': [dict(temperature_c=huge, humidity_pct=50, minutes_ahead=60)]})
        self.assertEqual(result['forecast']['invalid_rows'], 1)

    def test_bad_and_missing_inputs_cautious(self):
        for name, value in [('temperature_c', math.nan), ('humidity_pct', 101),
                            ('workload', 'unknown'), ('acclimatized', 'yes'),
                            ('duration_minutes', -1), ('sensor_age_seconds', True), ('emergency', 'false'), ('acknowledge', 'true')]:
            with self.subTest(name=name):
                r = evaluate({**BASE, name: value})
                self.assertEqual(r['data_quality'], 'invalid')
                self.assertNotEqual(r['level'], 'green')
        self.assertEqual(evaluate({})['data_quality'], 'invalid')

    def test_emergency_overrides_and_ack_does_not_clear(self):
        for state in [{'emergency': True}, {'emergency_latched': True}, {'previous_level': 'emergency'}]:
            r = evaluate({**BASE, **state, 'acknowledge': True})
            self.assertEqual(r['level'], 'emergency')
            self.assertTrue(r['emergency_latched'])
            self.assertTrue(r['acknowledged'])

    def test_forecast_escalates_cannot_lower_floor(self):
        r = evaluate({**BASE, 'forecast': [dict(temperature_c=40, humidity_pct=80, minutes_ahead=60)]})
        self.assertEqual(r['baseline_level'], 'green')
        self.assertEqual(r['level'], 'red')
        self.assertEqual(r['forecast']['minutes_to_illustrative_red'], 60)
        hot = evaluate({**BASE, 'temperature_c': 40, 'humidity_pct': 80,
                       'forecast': [dict(temperature_c=20, humidity_pct=20, minutes_ahead=60)]})
        self.assertEqual(hot['level'], 'red')

    def test_forecast_order_invalid_rows_and_no_state_mutation(self):
        source = {**BASE, 'forecast': [dict(temperature_c=40, humidity_pct=80, minutes_ahead=120),
                  None, dict(temperature_c=40, humidity_pct=80, minutes_ahead=30)]}
        self.assertEqual(evaluate(source)['forecast']['minutes_to_illustrative_red'], 30)
        self.assertEqual(evaluate(source)['forecast']['invalid_rows'], 1)
        self.assertEqual(len(source['forecast']), 3)


if __name__ == '__main__':
    unittest.main()
