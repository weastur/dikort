import copy
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from dikort.analyzer import (
    _finish,
    _generic_check,
    _open_repository,
    _process_failed_commits,
    analyze_commits,
)
from dikort.config import DEFAULTS, ERROR_EXIT_CODE, FAILED_EXIT_CODE


class TestCheck(TestCase):
    @patch("dikort.analyzer.print_error")
    @patch("sys.exit")
    def test_generic_check_fail(self, sys_exit_mock, print_error_mock):
        commit_range = MagicMock()
        commit_range.__iter__.side_effect = GitCommandError("test", 123)
        _generic_check(commit_range, None, check_merge_commits=False)
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    def test_generic_check_success(self):
        commit_range = [Mock(), Mock(), Mock()]
        commit_range[1].good = True
        commit_range[2].good = True
        commit_range[0].parents = []
        commit_range[1].parents = [Mock()]
        commit_range[2].parents = [Mock(), Mock()]
        actual_result = _generic_check(commit_range, lambda commit: commit.good, check_merge_commits=False)
        self.assertEqual(len(actual_result), 1)
        actual_result = _generic_check(commit_range, lambda commit: commit.good, check_merge_commits=True)
        self.assertEqual(len(actual_result), 1)


class TestAnalyzer(TestCase):
    @patch("dikort.analyzer.print_error")
    @patch("dikort.analyzer.print_success")
    @patch("sys.exit")
    def test_finish(self, sys_exit_mock, print_success_mock, print_error_mock):
        _finish(True)
        self.assertEqual(sys_exit_mock.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 0)
        print_success_mock.assert_called_once()

        print_success_mock.reset_mock()
        _finish(False)
        self.assertEqual(print_success_mock.call_count, 0)
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(FAILED_EXIT_CODE)

    @patch("sys.exit")
    @patch("dikort.analyzer.print_error")
    @patch("dikort.analyzer.Repo")
    def test_open_repository(self, repo_mock, print_error_mock, sys_exit_mock):
        config = {"main": {"repository": "./"}}
        repo_mock.side_effect = NoSuchPathError()
        _open_repository(config)
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_with(ERROR_EXIT_CODE)

        repo_mock.side_effect = InvalidGitRepositoryError()
        print_error_mock.reset_mock()
        sys_exit_mock.reset_mock()
        _open_repository(config)
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_with(ERROR_EXIT_CODE)

        repo_mock.side_effect = None
        print_error_mock.reset_mock()
        sys_exit_mock.reset_mock()
        _open_repository(config)
        repo_mock.assert_called_with(config["main"]["repository"])
        self.assertEqual(sys_exit_mock.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 0)

    @patch("dikort.analyzer.print_error")
    @patch("dikort.analyzer.print_success")
    def test_process_failed_commits(self, print_success_mock, print_error_mock):
        _process_failed_commits([], "rule")
        self.assertEqual(print_error_mock.call_count, 0)
        print_success_mock.assert_called_once()

        print_success_mock.reset_mock()
        _process_failed_commits([Mock()], "rule")
        self.assertEqual(print_success_mock.call_count, 0)
        print_error_mock.assert_called_once()

    @patch("dikort.analyzer._open_repository")
    @patch("dikort.analyzer._generic_check")
    @patch("dikort.analyzer._process_failed_commits")
    @patch("dikort.analyzer._finish")
    def test_analyze(
        self,
        _finish_mock,
        _process_failed_commits_mock,
        _generic_check_mock,
        _open_repository_mock,
    ):
        config = copy.deepcopy(DEFAULTS.copy())
        config["rules"]["enable_length"] = True
        repo = Mock()
        _open_repository_mock.return_value = repo
        _generic_check_mock.return_value = []
        _process_failed_commits_mock.return_value = False
        analyze_commits(config)
        _finish_mock.assert_called_with(False)
