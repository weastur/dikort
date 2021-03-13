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
    def test_check_for_new_version(self, mock_print_warning, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Fail")
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()

        mock_urlopen.reset_mock()
        mock_print_warning.reset_mock()
        mock_urlopen.side_effect = None
        releases = []
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

        mock_urlopen.reset_mock()
        mock_print_warning.reset_mock()
        releases = [{"tag_name": "v0.0.0"}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        self.assertEqual(mock_print_warning.call_count, 0)

        mock_urlopen.reset_mock()
        mock_print_warning.reset_mock()
        next_version = (
            "v" + dikort.__version__[:-1] + str(int(dikort.__version__[-1]) + 1)
        )
        releases = [{"tag_name": "v0.0.0"}, {"tag_name": next_version}]
        mock_urlopen.return_value = io.BytesIO(json.dumps(releases).encode())
        check_for_new_version()
        mock_urlopen.assert_called_once_with(GITHUB_RELEASES_API_URL, timeout=1)
        mock_print_warning.assert_called_once()
