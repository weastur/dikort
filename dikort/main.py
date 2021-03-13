import argparse
import json
import urllib.error
import urllib.request

import colorama

import dikort
from dikort.analyzer import analyze_commits
from dikort.config import configure_argparser, configure_logging, parse
from dikort.print import print_warning

GITHUB_RELEASES_API_URL = "https://api.github.com/repos/weastur/dikort/releases"


def check_for_new_version():
    try:
        with urllib.request.urlopen(GITHUB_RELEASES_API_URL, timeout=1) as resp:
            releases = json.loads(resp.read())
    except urllib.error.URLError as err:
        print_warning(f"Cannot check for new version. Error: {err}")
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


def main():  # pragma: nocover
    print("Welcome to dikort - the ultimate commit message check tool")
    colorama.init()
    check_for_new_version()

    cmd_args_parser = argparse.ArgumentParser(
        prog="dikort", description="Commit messages checking tool"
    )
    configure_argparser(cmd_args_parser)
    config = parse(cmd_args_parser.parse_args())
    configure_logging(config["logging"])
    analyze_commits(config)


if __name__ == "__main__":  # pragma: nocover
    main()
