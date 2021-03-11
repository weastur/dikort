import argparse

from dikort.config import parse, configure_logging


def main():
    parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    parser.add_argument(
        "-c", "--config", default="./.dikort.ini", help="Config file location"
    )
    args = vars(parser.parse_args())
    config = parse(args)
    configure_logging(config["logging"])
