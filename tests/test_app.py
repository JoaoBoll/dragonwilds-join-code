from pathlib import Path
from unittest import mock
import subprocess
import unittest

import app


class CompletedCommand:
    def __init__(self, stdout, returncode=0):
        self.stdout = stdout
        self.returncode = returncode


class JoinCodeWebTest(unittest.TestCase):
    def setUp(self):
        app._cached_code = None
        app._cached_at = 0.0

    @mock.patch("app.subprocess.run", return_value=CompletedCommand("PXQ5-8PF0\n"))
    def test_join_code_is_read_and_validated(self, run):
        self.assertEqual(app.read_join_code(), "PXQ5-8PF0")
        run.assert_called_once()
        self.assertEqual(app.REFRESH_COMMAND[-1], "/usr/local/libexec/dragonwilds-join-code")

    @mock.patch("app.subprocess.run", return_value=CompletedCommand("server logs and secrets\n"))
    def test_unexpected_output_is_not_exposed(self, _run):
        with self.assertRaisesRegex(RuntimeError, "unavailable"):
            app.read_join_code()

    @mock.patch("app.subprocess.run", side_effect=subprocess.TimeoutExpired("helper", 5))
    def test_helper_timeout_is_bounded(self, _run):
        with self.assertRaises(subprocess.TimeoutExpired):
            app.read_join_code()

    def test_page_contains_no_script_or_form(self):
        page = (Path(app.WEB_ROOT) / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<script", page)
        self.assertNotIn("<form", page)
        self.assertIn("{{JOIN_CODE}}", page)


if __name__ == "__main__":
    unittest.main()
