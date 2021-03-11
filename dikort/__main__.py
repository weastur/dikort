import argparse

from dikort.config import parse, configure_logging


def main():
    parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    parser.add_argument(
        "-c", "--config", default="./.dikort.cfg", help="Config file location"
    )
    config = parse(parser.parse_args())
    configure_logging(config["logging"])


main()
