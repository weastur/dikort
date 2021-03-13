from unittest import TestCase
from unittest.mock import patch

from colorama import Fore

from dikort.print import print_success, print_error, print_warning


class TestPrint(TestCase):

    @patch('builtins.print')
    def test_success(self, mock_print):
        line = "All clear"
        print_success(line)
        mock_print.assert_called_with(f"{Fore.GREEN}{line}{Fore.RESET}", end='\n')

    @patch('builtins.print')
    def test_error(self, mock_print):
        line = "All clear"
        print_error(line)
        mock_print.assert_called_with(f"{Fore.RED}{line}{Fore.RESET}", end='\n')

    @patch('builtins.print')
    def test_warning(self, mock_print):
        line = "All clear"
        print_warning(line)
        mock_print.assert_called_with(f"{Fore.YELLOW}{line}{Fore.RESET}", end='\n')