from unittest import TestCase
from unittest.mock import patch

from dikort.print import BColors, print_error, print_success, print_warning


class TestPrint(TestCase):
    @patch("builtins.print")
    def test_success(self, mock_print):
        line = "All clear"
        print_success(line)
        mock_print.assert_called_with(
            f"{BColors.OKGREEN}{line}{BColors.ENDC}", end="\n"
        )

    @patch("builtins.print")
    def test_error(self, mock_print):
        line = "All clear"
        print_error(line)
        mock_print.assert_called_with(
            f"{BColors.FAIL}{line}{BColors.ENDC}", end="\n"
        )

    @patch("builtins.print")
    def test_warning(self, mock_print):
        line = "All clear"
        print_warning(line)
        mock_print.assert_called_with(
            f"{BColors.WARNING}{line}{BColors.ENDC}", end="\n"
        )
