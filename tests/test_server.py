import json
import threading
import unittest
import urllib.error
import urllib.request
from exaclim.server import ROOT, make_server


class SupervisorSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = make_server()
        cls.base = f'http://127.0.0.1:{cls.httpd.server_port}'
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def test_health_identifies_synthetic_mode(self):
        with urllib.request.urlopen(self.base+'/api/health') as response:
            self.assertEqual(json.load(response)['mode'], 'synthetic-demo')

    def test_local_built_assets_and_fonts_are_served(self):
        paths = ['/', '/app.js', '/styles.css']
        for suffix in ('.js', '.woff2'):
            asset = next((ROOT/'assets').glob('*'+suffix), None)
            self.assertIsNotNone(asset, f'Build is missing {suffix} assets')
            paths.append('/assets/'+asset.name)
        for path in paths:
            with self.subTest(path=path), urllib.request.urlopen(self.base+path) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 10)

    def test_legacy_individual_worker_endpoints_are_removed(self):
        for path in ['/api/worker', '/api/crew', '/api/forecast', '/worker', '/system']:
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as failure:
                urllib.request.urlopen(self.base+path)
            self.assertEqual(failure.exception.code, 404)

    def test_asset_traversal_cannot_read_source_or_database(self):
        for path in ['/assets/../app.js', '/assets/../../exaclim/store.py', '/.local/exaclim-demo.sqlite3', '/AGENTS.md']:
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as failure:
                urllib.request.urlopen(self.base+path)
            self.assertEqual(failure.exception.code, 404)

    def test_csp_keeps_scripts_fonts_and_connections_local(self):
        with urllib.request.urlopen(self.base+'/') as response:
            policy = response.headers['Content-Security-Policy']
            self.assertIn("script-src 'self';", policy)
            self.assertIn("font-src 'self';", policy)
            self.assertIn("connect-src 'self';", policy)
            self.assertIn("frame-ancestors 'none'", policy)
