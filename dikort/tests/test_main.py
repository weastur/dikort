import io
import json
from unittest import TestCase
from unittest.mock import patch
from urllib.error import URLError

import dikort
from dikort.main import GITHUB_RELEASES_API_URL, check_for_new_version


class TestMain(TestCase):
    @patch("dikort.main.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_fail(self, mock_print_warning, mock_urlopen):
        mock_urlopen.side_effect = URLError("Fail")
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()

    @patch("dikort.main.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_empty_release_list(self, mock_print_warning, mock_urlopen):
        releases = []
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

    @patch("dikort.main.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_no_new_versions(self, mock_print_warning, mock_urlopen):
        releases = [{"tag_name": "v0.0.0"}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

    @patch("dikort.main.urlopen")
    @patch("dikort.main.print_warning")
    def test_check_for_new_version_success(self, mock_print_warning, mock_urlopen):
        current_version_value = dikort.__version__[:-1]
        current_version_minor_value = int(dikort.__version__[-1])
        next_version = "v" + current_version_value + str(current_version_minor_value + 1)
        releases = [{"tag_name": "v0.0.0"}, {"tag_name": next_version}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()
