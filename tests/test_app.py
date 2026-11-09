from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import app


class JoinCodeWebTest(unittest.TestCase):
    def setUp(self):
        app._cached_code = None
        app._cached_at = 0.0
        app._log_position = 0
        app._log_identity = None
        app._log_mtime_ns = None
        app._log_tail = b""

        self.temp_dir = TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp_dir.cleanup)
        app.LOG_FILE = Path(self.temp_dir.name) / "dragonwilds.log"

    def test_latest_join_code_is_returned(self):
        app.LOG_FILE.write_bytes(
            b'[1] Setting ["JoinCode"] written with key[xz] value[AAAA-BBBB]\n'
            b'[2] Setting ["JoinCode"] written with key[xz] value[PXQ5-8PF0]\n'
        )
        self.assertEqual(app.read_join_code(), "PXQ5-8PF0")

    def test_code_is_found_before_more_than_two_megabytes_of_later_logs(self):
        app.LOG_FILE.write_bytes(
            b'Setting ["JoinCode"] written with key[xz] value[VKAN-93V4]\n'
            + b"ordinary log line\n" * 150_000
        )
        self.assertEqual(app.read_join_code(), "VKAN-93V4")

    def test_appended_code_replaces_cached_code(self):
        app.LOG_FILE.write_bytes(
            b'Setting ["JoinCode"] written with key[xz] value[AAAA-BBBB]\n'
        )
        self.assertEqual(app.read_join_code(), "AAAA-BBBB")

        with app.LOG_FILE.open("ab") as log:
            log.write(
                b'Setting ["JoinCode"] written with key[xz] value[CCCC-DDDD]\n'
            )
        app._cached_at = 0.0
        self.assertEqual(app.read_join_code(), "CCCC-DDDD")

    def test_truncated_log_does_not_return_stale_code(self):
        app.LOG_FILE.write_bytes(
            b'Setting ["JoinCode"] written with key[xz] value[AAAA-BBBB]\n'
        )
        self.assertEqual(app.read_join_code(), "AAAA-BBBB")

        app.LOG_FILE.write_bytes(b"new server session without a code yet\n")
        app._cached_at = 0.0
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    def test_other_log_data_is_not_exposed(self):
        app.LOG_FILE.write_bytes(b"server logs and secrets\n")
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    def test_missing_log_is_reported_as_unavailable(self):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    def test_page_contains_no_script_or_form(self):
        page = (Path(app.WEB_ROOT) / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", page)
        self.assertNotIn("<form", page)
        self.assertIn("{{JOIN_CODE}}", page)


if __name__ == "__main__":
    unittest.main()
