class BColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.HEADER)


def print_error(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.FAIL)


def print_warning(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.WARNING)


def print_success(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.OKGREEN)


def _print_formatted(*args, sep=" ", end="\n", formatter=None):
    line = sep.join(args)
    print(f"{formatter}{line}{BColors.ENDC}", end=end)
