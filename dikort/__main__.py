import argparse
import logging

from dikort.config import parse


def main():
    parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    parser.add_argument(
        "-c", "--config", default="./.dikort.ini", help="Config file location"
    )
    args = vars(parser.parse_args())
    print(args)
    parse(args["config"])
    logging.info("test")
