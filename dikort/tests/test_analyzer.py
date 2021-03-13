from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from git.exc import GitCommandError

from dikort.analyzer import _generic_check, analyze_commits
from dikort.config import ERROR_EXIT_CODE


class TestAnalyzer(TestCase):
    @patch("dikort.analyzer.print_error")
    @patch("sys.exit")
    def test_generic_check(self, sys_exit_mock, print_error_mock):
        commit_range = MagicMock()
        commit_range.__iter__.side_effect = GitCommandError("test", 123)
        _generic_check(commit_range, None)
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

        commit_range = [Mock(), Mock(), Mock()]
        commit_range[1].good = True
        commit_range[2].good = True
        commit_range[0].parents = []
        commit_range[1].parents = [Mock()]
        commit_range[2].parents = []
        result = _generic_check(commit_range, lambda commit: commit.good)
        self.assertEqual(len(result), 1)
