import argparse
import configparser
import copy
from unittest import TestCase
from unittest.mock import Mock, patch

from dikort.config import (
    DEFAULTS,
    ERROR_EXIT_CODE,
    _from_cmd_args_to_config,
    _merge_fileconfig,
    _parse_value_from_file,
    _post_processing,
    _read_file_config,
    _validate,
    configure_argparser,
    merge,
)


class TestValidators(TestCase):
    def setUp(self):
        self.config = {
            "rules.settings": {
                "min_length": 10,
                "max_length": 100,
            },
            "merge_rules.settings": {
                "min_length": 10,
                "max_length": 100,
            },
        }

    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_validate_success(self, sys_exit_mock, print_error_mock):
        _validate(self.config)
        self.assertEqual(sys_exit_mock.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 0)

    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_validate_error_rules(self, sys_exit_mock, print_error_mock):
        self.config["rules.settings"]["min_length"] = 128
        _validate(self.config)
        self.assertEqual(print_error_mock.call_count, 1)
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_validate_error_merge_rules(self, sys_exit_mock, print_error_mock):
        self.config["merge_rules.settings"]["min_length"] = 128
        _validate(self.config)
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)
        self.assertEqual(print_error_mock.call_count, 1)


class TestFileConfig(TestCase):
    @patch("builtins.open")
    def test_read_file_success(self, open_mock):
        configparser_instance = Mock()
        _read_file_config(configparser_instance, DEFAULTS["main"]["config"])
        configparser_instance.read_file.assert_called_once()

    @patch("builtins.open")
    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_read_file_notfound(self, sys_exit_mock, print_error_mock, open_mock):
        open_mock.side_effect = FileNotFoundError()
        configparser_instance = Mock()
        _read_file_config(configparser_instance, DEFAULTS["main"]["config"])
        self.assertEqual(configparser_instance.read_file.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 0)
        self.assertEqual(sys_exit_mock.call_count, 0)

        sys_exit_mock.reset_mock()
        print_error_mock.reset_mock()
        configparser_instance.reset_mock()
        open_mock.side_effect = FileNotFoundError()
        _read_file_config(configparser_instance, "/tmp/.dikort.cfg")
        self.assertEqual(configparser_instance.read_file.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 1)
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("builtins.open")
    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_read_file_error(self, sys_exit_mock, print_error_mock, open_mock):
        open_mock.side_effect = OSError()
        configparser_instance = Mock()
        _read_file_config(configparser_instance, DEFAULTS["main"]["config"])
        self.assertEqual(configparser_instance.read_file.call_count, 0)
        self.assertEqual(print_error_mock.call_count, 1)
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)


class TestMerge(TestCase):
    def test_post_processing(self):
        config = copy.deepcopy(DEFAULTS.copy())
        _post_processing(config)
        self.assertEqual(
            config["rules.settings"]["regex"].pattern,
            DEFAULTS["rules.settings"]["regex"],
        )
        self.assertEqual(
            config["rules.settings"]["author_name_regex"].pattern,
            DEFAULTS["rules.settings"]["author_name_regex"],
        )
        self.assertEqual(
            config["rules.settings"]["author_email_regex"].pattern,
            DEFAULTS["rules.settings"]["author_email_regex"],
        )
        self.assertEqual(
            config["merge_rules.settings"]["author_email_regex"].pattern,
            DEFAULTS["merge_rules.settings"]["author_email_regex"],
        )
        self.assertEqual(
            config["merge_rules.settings"]["author_name_regex"].pattern,
            DEFAULTS["merge_rules.settings"]["author_name_regex"],
        )
        self.assertEqual(
            config["merge_rules.settings"]["regex"].pattern,
            DEFAULTS["merge_rules.settings"]["regex"],
        )

    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_parse_value_from_file_success(self, sys_exit_mock, print_error_mock):
        config = configparser.ConfigParser(interpolation=None)
        config.add_section("logging")
        config.add_section("rules.settings")
        config["logging"]["enabled"] = "yes"
        config["rules.settings"]["min_length"] = "5"
        config["logging"]["format"] = "format"
        self.assertEqual(_parse_value_from_file(config, "enabled", "logging"), True)
        self.assertEqual(_parse_value_from_file(config, "format", "logging"), "format")
        self.assertEqual(_parse_value_from_file(config, "min_length", "rules.settings"), 5)
        self.assertEqual(print_error_mock.call_count, 0)
        self.assertEqual(sys_exit_mock.call_count, 0)

    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_parse_value_from_file_error(self, sys_exit_mock, print_error_mock):
        config = configparser.ConfigParser(interpolation=None)
        config.add_section("rules.settings")
        config["rules.settings"]["min_length"] = "five"
        _parse_value_from_file(config, "min_length", "rules.settings")
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("dikort.config._read_file_config")
    def test_merge_fileconfig(self, _read_file_config_mock):
        def _side_effect(file_config, file_config_path):
            file_config.add_section("logging")
            file_config.add_section("rules")
            file_config["logging"]["enabled"] = "yes"
            file_config["rules"]["regex"] = "yes"

        config = {
            "logging": {
                "enabled": False,
            },
            "rules": {
                "regex": False,
                "signoff": False,
            },
            "rules.settings": {"regex": ".*"},
        }
        _read_file_config_mock.side_effect = _side_effect
        _merge_fileconfig(config, "/tmp/.dikort.cfg")

    @patch("dikort.config._merge_fileconfig")
    @patch("dikort.config._from_cmd_args_to_config")
    @patch("dikort.config._validate")
    @patch("dikort.config._post_processing")
    def test_merge(
        self,
        _post_processing_mock,
        _validate_mock,
        _from_cmd_args_to_config_mock,
        _merge_fileconfig_mock,
    ):
        expected_result_config = copy.deepcopy(DEFAULTS.copy())
        expected_result_config["rules.settings"]["regex"] = r"ISSUE-\d+: .*"
        _from_cmd_args_to_config_mock.return_value = {
            "rules.settings": {
                "regex": r"ISSUE-\d+: .*",
            }
        }

        cmd_args_parser = argparse.ArgumentParser()
        configure_argparser(cmd_args_parser)
        cmd_args = cmd_args_parser.parse_args([r"--regex 'ISSUE-\d+: .*'"])

        actual_result_config = merge(cmd_args)

        self.assertDictEqual(actual_result_config, expected_result_config)
        _merge_fileconfig_mock.assert_called_once()
        _from_cmd_args_to_config_mock.assert_called_once_with(cmd_args)
        _validate_mock.assert_called_once_with(expected_result_config)
        _post_processing_mock.assert_called_once_with(expected_result_config)


class TestCmdArgs(TestCase):
    def test_from_cmd_args_to_config(self):
        cmd_args_parser = argparse.ArgumentParser()
        configure_argparser(cmd_args_parser)
        cmd_args = cmd_args_parser.parse_args(["--config=/tmp/.dikort.cfg", "--enable-logging", "HEAD~1..HEAD"])
        expected_config = {
            "logging": {
                "enabled": True,
            },
            "main": {
                "config": "/tmp/.dikort.cfg",
                "range": "HEAD~1..HEAD",
            },
        }
        actual_config = _from_cmd_args_to_config(cmd_args)
        self.assertDictEqual(actual_config, expected_config)
