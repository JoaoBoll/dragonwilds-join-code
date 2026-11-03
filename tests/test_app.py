from io import BytesIO
from pathlib import Path
from unittest import mock
import unittest

import app


class JoinCodeWebTest(unittest.TestCase):
    def setUp(self):
        app._cached_code = None
        app._cached_at = 0.0

    @mock.patch.object(
        app.Path,
        "open",
        return_value=BytesIO(
            b'[1] Setting ["JoinCode"] written with key[xz] value[AAAA-BBBB]\n'
            b'[2] Setting ["JoinCode"] written with key[xz] value[PXQ5-8PF0]\n'
        )
    )
    def test_latest_join_code_is_returned(self, _open):
        self.assertEqual(app.read_join_code(), "PXQ5-8PF0")

    @mock.patch.object(app.Path, "open", return_value=BytesIO(b"server logs and secrets\n"))
    def test_other_log_data_is_not_exposed(self, _open):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    @mock.patch.object(app.Path, "open", side_effect=FileNotFoundError)
    def test_missing_log_is_reported_as_unavailable(self, _open):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    def test_page_contains_no_script_or_form(self):
        page = (Path(app.WEB_ROOT) / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", page)
        self.assertNotIn("<form", page)
        self.assertIn("{{JOIN_CODE}}", page)


if __name__ == "__main__":
    unittest.main()
