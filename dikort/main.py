import argparse
import json
import logging
from urllib.error import URLError
from urllib.request import urlopen

import dikort
from dikort.analyzer import analyze_commits
from dikort.config import configure_argparser, merge
from dikort.print import print_header, print_warning

GITHUB_RELEASES_API_URL = "https://api.github.com/repos/weastur/dikort/releases"


def check_for_new_version():
    try:
        with urlopen(GITHUB_RELEASES_API_URL, timeout=1) as resp:
            releases = json.loads(resp.read())
    except URLError as err:
        print_warning(f"Cannot check for new version. Error: {err}")
        return
    tags = [release["tag_name"] for release in releases]
    if not tags:
        return
    tags.sort()
    latest_tag = tags[-1][1:]
    if dikort.__version__ < latest_tag:
        print_warning(f"There is a new version: {latest_tag}. Please, consider to update")


def main():  # pragma: nocover
    print_header("Welcome to dikort - the ultimate commit message check tool")
    check_for_new_version()
    cmd_args_parser = argparse.ArgumentParser(prog="dikort", description="Commit messages checking tool")
    configure_argparser(cmd_args_parser)
    config = merge(cmd_args_parser.parse_args())
    logging_config = {
        "format": config["logging"]["format"],
        "level": config["logging"]["level"],
        "datefmt": config["logging"]["datefmt"],
    }
    if not config["logging"]["enabled"]:
        logging_config["handlers"] = [logging.NullHandler()]
    logging.basicConfig(**logging_config)
    analyze_commits(config)


if __name__ == "__main__":  # pragma: nocover
    main()
