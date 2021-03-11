import argparse
import colorama

from dikort.config import parse, configure_logging


def main():
    colorama.init()
    cmd_args_parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    cmd_args_parser.add_argument(
        "-c", "--config", default="./.dikort.cfg", help="Config file location"
    )
    config = parse(cmd_args_parser.parse_args())
    configure_logging(config["logging"])


if __name__ == "__main__":
    main()
