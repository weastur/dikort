from colorama import Fore


def print_error(*args, sep=" ", end="\n"):
    line = sep.join(args)
    print(f"{Fore.RED}{line}{Fore.RESET}", end=end)


def print_warning(*args, sep=" ", end="\n"):
    line = sep.join(args)
    print(f"{Fore.YELLOW}{line}{Fore.RESET}", end=end)
