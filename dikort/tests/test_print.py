from unittest import TestCase
from unittest.mock import patch

from dikort.print import (
    BColors,
    _print_formatted,
    print_error,
    print_header,
    print_success,
    print_warning,
)


class TestPrint(TestCase):
    @patch("builtins.print")
    def test_print_formatted(self, mock_print):
        line = "OK"
        _print_formatted(line, formatter=BColors.okgreen)
        mock_print.assert_called_once_with(f"{BColors.okgreen}{line}{BColors.endc}", end="\n")

    @patch("dikort.print._print_formatted")
    def test_success(self, mock_print):
        line = "All clear"
        print_success(line)
        mock_print.assert_called_once_with(line, sep=" ", end="\n", formatter=BColors.okgreen)

    @patch("dikort.print._print_formatted")
    def test_error(self, mock_print):
        line = "Error"
        print_error(line)
        mock_print.assert_called_once_with(line, sep=" ", end="\n", formatter=BColors.fail)

    @patch("dikort.print._print_formatted")
    def test_warning(self, mock_print):
        line = "Warning"
        print_warning(line)
        mock_print.assert_called_once_with(line, sep=" ", end="\n", formatter=BColors.warning)

    @patch("dikort.print._print_formatted")
    def test_header(self, mock_print):
        line = "Hello!"
        print_header(line)
        mock_print.assert_called_once_with(line, sep=" ", end="\n", formatter=BColors.header)
