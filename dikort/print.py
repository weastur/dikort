class BColors:
    header = "\033[95m"
    okgreen = "\033[92m"
    warning = "\033[93m"
    fail = "\033[91m"
    endc = "\033[0m"


def print_header(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.header)


def print_error(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.fail)


def print_warning(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.warning)


def print_success(*args, sep=" ", end="\n"):
    _print_formatted(*args, sep=sep, end=end, formatter=BColors.okgreen)


def _print_formatted(*args, sep=" ", end="\n", formatter=None):
    line = sep.join(args)
    print(f"{formatter}{line}{BColors.endc}", end=end)
