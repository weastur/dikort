import configparser
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from dikort.analyzer import _generic_check, analyze_commits
from dikort.config import DEFAULTS, ERROR_EXIT_CODE, FAILED_EXIT_CODE


def _positive_filter(commit, *, config):
    return True


def _negative_filter(commit, *, config):
    return True


class TestAnalyzer(TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read_dict(DEFAULTS)

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

    @patch("dikort.analyzer.print_error")
    @patch("sys.exit")
    @patch("dikort.analyzer.Repo")
    def test_analyze_commits_git_fail(
        self, repo_mock, sys_exit_mock, print_error_mock
    ):
        repo_mock.side_effect = InvalidGitRepositoryError()
        sys_exit_mock.side_effect = Exception
        try:
            analyze_commits(self.config)
        except Exception:
            pass
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

        repo_mock.side_effect = NoSuchPathError()
        print_error_mock.reset_mock()
        sys_exit_mock.reset_mock()
        sys_exit_mock.side_effect = Exception
        try:
            analyze_commits(self.config)
        except Exception:
            pass
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("dikort.analyzer.print_success")
    @patch("dikort.analyzer.print_error")
    @patch("dikort.analyzer.Repo")
    def test_analyze_commits_all_clear(
        self, repo_mock, print_error_mock, print_success_mock
    ):
        rules = {
            "Summary length": {
                "param": "length",
                "filter": _negative_filter,
            },
            "Trailing period": {
                "param": "trailing-period",
                "filter": _positive_filter,
            },
        }
        self.config["rules"]["trailing-period"] = "no"
        with patch("dikort.analyzer.RULES", rules):
            analyze_commits(self.config)
        self.assertEqual(print_success_mock.call_count, 2)
        self.assertEqual(print_error_mock.call_count, 0)

    @patch("dikort.analyzer.print_success")
    @patch("dikort.analyzer.print_error")
    @patch("dikort.analyzer.Repo")
    @patch("dikort.analyzer._generic_check")
    @patch("sys.exit")
    def test_analyze_commits_failed(
        self,
        sys_exit_mock,
        _generic_check_mock,
        repo_mock,
        print_error_mock,
        print_success_mock,
    ):
        rules = {
            "Summary length": {
                "param": "length",
                "filter": _positive_filter,
            },
            "Trailing period": {
                "param": "trailing-period",
                "filter": _positive_filter,
            },
        }
        self.config["rules"]["trailing-period"] = "no"
        _generic_check_mock.return_value = [Mock()]
        with patch("dikort.analyzer.RULES", rules):
            analyze_commits(self.config)
        _generic_check_mock.assert_called_once()
        self.assertEqual(print_success_mock.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 2)
        sys_exit_mock.assert_called_once_with(FAILED_EXIT_CODE)
