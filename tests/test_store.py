import concurrent.futures
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exaclim.store import DEMO_EMAIL, DEMO_PASSWORD, Store


def initial():
    return {"events": [{"id": "help-1", "acknowledged": False}], "counter": 0}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "state.sqlite3"
        self.store = Store(self.path, initial)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_load_is_detached_and_update_returns_mutator_result(self):
        state = self.store.load()
        state["events"].clear()
        self.assertEqual(len(self.store.load()["events"]), 1)
        def ack(state):
            state["events"][0].update(acknowledged=True, acknowledged_by="demo-supervisor")
            return state["events"][0]
        result = self.store.update(ack)
        result["acknowledged"] = False
        self.assertTrue(self.store.load()["events"][0]["acknowledged"])

    def test_update_exception_and_invalid_json_roll_back(self):
        def fail(state):
            state["counter"] = 9
            raise RuntimeError("failed ACK")
        with self.assertRaises(RuntimeError):
            self.store.update(fail)
        self.assertEqual(self.store.load()["counter"], 0)
        with self.assertRaises(ValueError):
            self.store.update(lambda state: state.update(counter=float("nan")))
        self.assertEqual(self.store.load()["counter"], 0)

    def test_restart_preserves_state_ack_and_sessions(self):
        token = self.store.authenticate(DEMO_EMAIL, DEMO_PASSWORD)
        self.store.update(lambda state: state["events"][0].update(acknowledged=True))
        self.store.close()
        self.store = Store(self.path, lambda: {"wrong": "must not overwrite"})
        self.assertTrue(self.store.load()["events"][0]["acknowledged"])
        self.assertEqual(self.store.user_for_session(token)["email"], DEMO_EMAIL)

    def test_concurrent_updates_across_connections_have_no_lost_writes(self):
        other = Store(self.path, initial)
        try:
            def increment(index):
                store = self.store if index % 2 else other
                store.update(lambda state: state.update(counter=state["counter"] + 1))
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(increment, range(80)))
            self.assertEqual(self.store.load()["counter"], 80)
        finally:
            other.close()

    def test_wrong_password_unknown_user_and_invalid_session(self):
        self.assertIsNone(self.store.authenticate(DEMO_EMAIL, "wrong"))
        self.assertIsNone(self.store.authenticate("unknown@exaclim.test", DEMO_PASSWORD))
        self.assertIsNone(self.store.user_for_session("bogus"))
        self.assertIsNone(self.store.user_for_session(None))

    def test_login_scope_grant_logout_and_no_raw_session_storage(self):
        token = self.store.authenticate(" DEMO@EXACLIM.TEST ", DEMO_PASSWORD)
        self.assertIsInstance(token, str)
        self.assertEqual(self.store.user_for_session(token)["site_ids"], ["accra", "tema"])
        self.store.grant_site(token, "new-site")
        self.store.grant_site(token, "new-site")
        self.assertEqual(self.store.user_for_session(token)["site_ids"].count("new-site"), 1)
        with sqlite3.connect(self.path) as conn:
            session_hash = conn.execute("SELECT token_hash FROM sessions").fetchone()[0]
            self.assertNotEqual(session_hash, token)
            record = conn.execute("SELECT password_hash FROM users").fetchone()[0]
            self.assertNotEqual(record, DEMO_PASSWORD.encode())
            self.assertNotIn(DEMO_PASSWORD, json.dumps(self.store.load()))
        self.store.logout(token)
        self.assertIsNone(self.store.user_for_session(token))
        self.assertIsNone(self.store.grant_site(token, "forbidden"))

    def test_expired_session_rejected(self):
        token = self.store.authenticate(DEMO_EMAIL, DEMO_PASSWORD)
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE sessions SET expires_at=?", ("2000-01-01T00:00:00+00:00",))
        self.assertIsNone(self.store.user_for_session(token))

    def test_memory_store_keeps_connection_and_reset_is_explicit(self):
        memory = Store(":memory:", initial)
        try:
            self.assertIsNone(memory.update(lambda state: state.update(counter=7)))
            self.assertEqual(memory.load()["counter"], 7)
            self.assertEqual(memory.reset()["counter"], 0)
        finally:
            memory.close()


if __name__ == "__main__":
    unittest.main()
