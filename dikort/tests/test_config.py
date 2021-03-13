import configparser
from unittest import TestCase
from unittest.mock import Mock, patch

from dikort.config import (
    ERROR_EXIT_CODE,
    _validate_bool,
    _validate_int,
    configure_logging,
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
