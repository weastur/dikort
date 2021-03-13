import argparse
import configparser
import io
from unittest import TestCase
from unittest.mock import Mock, patch

from dikort.config import (
    DEFAULTS,
    ERROR_EXIT_CODE,
    _validate_bool,
    _validate_int,
    configure_argparser,
    configure_logging,
    from_cmd_args_to_config,
    parse,
    validate,
)


class TestValidators(TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.add_section("correct")
        self.config.add_section("incorrect")

    @patch("sys.exit")
    @patch("dikort.config.print_error")
    def test_validate_bool(self, print_error_mock, sys_exit_mock):
        self.config["correct"]["key"] = "yes"
        self.config["incorrect"]["key"] = "okay"

        _validate_bool(self.config["correct"], "key")
        self.assertEqual(print_error_mock.call_count, 0)
        self.assertEqual(sys_exit_mock.call_count, 0)

        _validate_bool(self.config["incorrect"], "key")
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("sys.exit")
    @patch("dikort.config.print_error")
    def test_validate_int(self, print_error_mock, sys_exit_mock):
        self.config["correct"]["key"] = "6"
        self.config["incorrect"]["key"] = "six"

        _validate_int(self.config["correct"], "key")
        self.assertEqual(print_error_mock.call_count, 0)
        self.assertEqual(sys_exit_mock.call_count, 0)

        _validate_int(self.config["incorrect"], "key")
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)

    @patch("dikort.config._validate_int")
    @patch("dikort.config._validate_bool")
    def test_validate(self, validate_bool_mock, validate_int_mock):
        self.config.remove_section("correct")
        self.config.remove_section("incorrect")
        config = {
            "rules": {
                "length": "yes",
            },
            "rules.settings": {
                "capitalized-summary": "yes",
                "trailing-period": "yes",
                "gpg": "yes",
                "signoff": "yes",
                "singleline-summary": "yes",
                "min-length": "10",
                "max-length": "100",
            },
            "logging": {"enabled": "no"},
        }
        self.config.read_dict(config)
        validate(self.config)
        self.assertEqual(validate_int_mock.call_count, 2)
        self.assertEqual(validate_bool_mock.call_count, 7)


class TestLogging(TestCase):
    @patch("logging.basicConfig")
    @patch("logging.NullHandler")
    def test_configure_logging(self, null_handler_mock, basic_config_mock):
        null_handler_instance = Mock()
        null_handler_mock.return_value = null_handler_instance

        config = configparser.ConfigParser(interpolation=None)
        python_config = {
            "format": "%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s",
            "level": "DEBUG",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
        logging_config = {
            "logging": {
                "enabled": "no",
            }
        }
        logging_config["logging"].update(python_config)
        config.read_dict(logging_config)

        configure_logging(config["logging"])
        python_config["handlers"] = [null_handler_instance]
        null_handler_mock.assert_called_once()
        basic_config_mock.assert_called_once_with(**python_config)

        null_handler_mock.reset_mock()
        basic_config_mock.reset_mock()
        config["logging"]["enabled"] = "yes"
        python_config.pop("handlers")
        configure_logging(config["logging"])
        self.assertEqual(null_handler_mock.call_count, 0)
        basic_config_mock.assert_called_once_with(**python_config)


class TestParsing(TestCase):
    def _assert_configs_equals(self, config_1, config_2):
        self.assertListEqual(config_1.sections(), config_2.sections())
        for section in config_1.sections():
            self.assertEqual(
                len(config_1.options(section)), len(config_2.options(section))
            )
            for option in config_1.options(section):
                self.assertEqual(
                    config_1[section][option], config_2[section][option]
                )

    def test_from_cmdargs_to_config(self):
        parser = argparse.ArgumentParser()
        configure_argparser(parser)
        result = from_cmd_args_to_config(
            parser.parse_args(["--config=./myconfig.cfg", "--min-length=20"])
        )
        self.assertDictEqual(
            result,
            {
                "rules": {},
                "rules.settings": {
                    "min-length": 20,
                },
                "main": {
                    "config": "./myconfig.cfg",
                },
            },
        )

        result = from_cmd_args_to_config(parser.parse_args(["--enable-length"]))
        self.assertDictEqual(
            result,
            {
                "rules": {"length": True},
                "rules.settings": {},
                "main": {},
            },
        )

    @patch("builtins.open")
    @patch("dikort.config.print_error")
    @patch("sys.exit")
    def test_parse(self, sys_exit_mock, print_error_mock, open_mock):
        expected_config = configparser.ConfigParser(interpolation=None)
        expected_config.read_dict(DEFAULTS)
        parser = argparse.ArgumentParser()
        configure_argparser(parser)

        open_mock.return_value = io.StringIO()
        config = parse(parser.parse_args([]))
        self._assert_configs_equals(config, expected_config)

        open_mock.assert_called_once()
        self.assertEqual(print_error_mock.call_count, 0)

        open_mock.reset_mock()
        print_error_mock.reset_mock()
        open_mock.side_effect = OSError("ops!")
        config = parse(parser.parse_args([]))
        print_error_mock.assert_called_once()
        sys_exit_mock.assert_called_once_with(ERROR_EXIT_CODE)
