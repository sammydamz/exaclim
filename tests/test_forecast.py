import datetime as dt
import io
import json
import unittest
from exaclim.forecast import live

class ForecastTests(unittest.TestCase):
    def response(self, **changes):
        now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
        data = {'time':[(now+dt.timedelta(hours=i)).replace(tzinfo=None).isoformat() for i in range(4)],
                'temperature_2m':[29,30,31,30], 'relative_humidity_2m':[60,59,58,60]}
        data.update(changes)
        return lambda *a, **k: io.BytesIO(json.dumps({'hourly':data}).encode())

    def test_live_adapter_preserves_source_and_freshness(self):
        result = live(self.response())
        self.assertEqual(result['status'],'live')
        self.assertEqual(len(result['hourly']),4)
        self.assertTrue(result['fetched_at'])
        self.assertIn('not measured site',result['limitation'])

    def test_missing_misaligned_null_and_nonfinite_values_rejected(self):
        for changes in [{'temperature_2m':[]}, {'temperature_2m':[None]*4},
                        {'temperature_2m':[float('inf')]*4}, {'relative_humidity_2m':[120]*4}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                live(self.response(**changes))

    def test_expired_forecast_rejected(self):
        with self.assertRaises(ValueError):
            live(self.response(time=['2000-01-01T00:00']*4))
