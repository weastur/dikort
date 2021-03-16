import io
import json
import urllib.error
from unittest import TestCase
from unittest.mock import patch

import dikort
from dikort.main import GITHUB_RELEASES_API_URL, check_for_new_version


class TestMain(TestCase):
    @patch("dikort.main.urllib.request.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_fail(self, mock_print_warning, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Fail")
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()

    @patch("dikort.main.urllib.request.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_empty_release_list(
        self, mock_print_warning, mock_urlopen
    ):
        releases = []
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

    @patch("dikort.main.urllib.request.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_no_new_versions(
        self, mock_print_warning, mock_urlopen
    ):
        releases = [{"tag_name": "v0.0.0"}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

    @patch("dikort.main.urllib.request.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_success(
        self, mock_print_warning, mock_urlopen
    ):
        next_version = (
            "v" + dikort.__version__[:-1] + str(int(dikort.__version__[-1]) + 1)
        )
        releases = [{"tag_name": "v0.0.0"}, {"tag_name": next_version}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()
