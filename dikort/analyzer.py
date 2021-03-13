import functools
import logging
import sys

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from dikort.config import ERROR_EXIT_CODE, FAILED_EXIT_CODE
from dikort.filters import (
    _filter_author_email_regex,
    _filter_author_name_regex,
    _filter_capitalized,
    _filter_gpg,
    _filter_length,
    _filter_regex,
    _filter_signoff,
    _filter_singleline,
    _filter_trailing_period,
)
from dikort.print import print_error, print_success

RULES = {
    "Summary length": {
        "param": "length",
        "filter": _filter_length,
    },
    "Trailing period": {
        "param": "trailing-period",
        "filter": _filter_trailing_period,
    },
    "Capitalized summary": {
        "param": "capitalized-summary",
        "filter": _filter_capitalized,
    },
    "Signle line summary": {
        "param": "singleline-summary",
        "filter": _filter_singleline,
    },
    "Signoff": {
        "param": "signoff",
        "filter": _filter_signoff,
    },
    "GPG": {
        "param": "gpg",
        "filter": _filter_gpg,
    },
    "Regex": {
        "param": "regex",
        "filter": _filter_regex,
    },
    "Author name regex": {
        "param": "author-name-regex",
        "filter": _filter_author_name_regex,
    },
    "Author email regex": {
        "param": "author-email-regex",
        "filter": _filter_author_email_regex,
    },
}


def _generic_check(commit_range, predicate):
    try:
        return list(
            filter(
                predicate,
                filter(lambda commit: len(commit.parents) == 1, commit_range),
            )
        )
    except GitCommandError as err:
        print_error(f"Cannot read commit in rage. Error: {err}")
        sys.exit(ERROR_EXIT_CODE)


def analyze_commits(config):
    logging.info("Start checks")
    repository_path = config["main"]["repository"]
    logging.debug("Open repo at %s", repository_path)
    try:
        repo = Repo(repository_path)
    except (NoSuchPathError, InvalidGitRepositoryError) as err:
        print_error(f"Cannot open git repo at {repository_path}. Error: {err}")
        sys.exit(ERROR_EXIT_CODE)
    all_clear = True
    for rule in RULES:
        if not config["rules"].getboolean(RULES[rule]["param"]):
            logging.info("Rule '%s' disabled. Skip.", rule)
            continue
        logging.debug("Rule '%s' enabled. Start.", rule)
        print(f"[{rule}] - ", end="")
        predicate = functools.partial(RULES[rule]["filter"], config=config)
        failed = _generic_check(
            repo.iter_commits(rev=config["main"]["range"]), predicate
        )
        if failed:
            print_error("ERROR")
            all_clear = False
            logging.info("Failed %d commit for '%s' rule", len(failed), rule)
            for commit in failed:
                logging.debug(
                    "Hash: %s, message: '%s'", commit.hexsha, commit.summary
                )
                print(f"Hash: {commit.hexsha}, message: '{commit.summary}'")
        else:
            logging.info("Errors not found for rule '%s'", rule)
            print_success("SUCCESS")
    if all_clear:
        logging.info("All clear.")
        print_success("All clear.")
    else:
        print_error("Some checks are failed.")
        logging.info("Some checks are failed.")
        logging.info("Exit with state %d", FAILED_EXIT_CODE)
        sys.exit(FAILED_EXIT_CODE)
