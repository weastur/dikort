import argparse
import json
import logging
import urllib.error
import urllib.request

import colorama

import dikort
from dikort.analyzer import check
from dikort.config import configure_logging, parse
from dikort.print import print_warning

GITHUB_RELEASES_API_URL = "https://api.github.com/repos/weastur/dikort/releases"


def check_for_new_version():
    try:
        with urllib.request.urlopen(GITHUB_RELEASES_API_URL, timeout=1) as resp:
            releases = json.loads(resp.read())
    except urllib.error.URLError as err:
        logging.error("Cannot check for a new version, error: %s", err)
        return
    tags = [release["tag_name"] for release in releases]
    if not tags:
        return
    tags.sort()
    latest_tag = tags[-1][1:]
    if dikort.__version__ < latest_tag:
        print_warning(
            f"There is a new version: {latest_tag}. Please, consider to update"
        )


def main():
    colorama.init()
    check_for_new_version()

    cmd_args_parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    cmd_args_parser.add_argument(
        "-c", "--config", default="./.dikort.cfg", help="Config file location"
    )
    cmd_args_parser.add_argument(
        "-r", "--repository", default="./", help="Repository location"
    )
    cmd_args_parser.add_argument(
        "--min-length", default=10, type=int, help="Minimum commit length"
    )
    cmd_args_parser.add_argument(
        "--max-length", default=50, type=int, help="Maximum commit length"
    )
    cmd_args_parser.add_argument(
        "--capitalized-summary",
        default=True,
        type=bool,
        help="Check is summary message capitalized",
    )
    cmd_args_parser.add_argument(
        "--trailing-period",
        default=False,
        type=bool,
        help="Check for trailing period",
    )
    cmd_args_parser.add_argument(
        "range", nargs="?", default="HEAD", help="Commit range"
    )
    config = parse(cmd_args_parser.parse_args())

    configure_logging(config["logging"])
    check(config)


if __name__ == "__main__":
    main()
