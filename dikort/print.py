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


def print_error(*args, sep=" ", end="\n"):
    line = sep.join(args)
    print(f"{BColors.FAIL}{line}{BColors.ENDC}", end=end)


def print_warning(*args, sep=" ", end="\n"):
    line = sep.join(args)
    print(f"{BColors.WARNING}{line}{BColors.ENDC}", end=end)


def print_success(*args, sep=" ", end="\n"):
    line = sep.join(args)
    print(f"{BColors.OKGREEN}{line}{BColors.ENDC}", end=end)
