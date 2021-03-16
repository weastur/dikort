import functools
import logging
import sys

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from dikort.config import ERROR_EXIT_CODE, FAILED_EXIT_CODE
from dikort.filters import (
    filter_author_email_regex,
    filter_author_name_regex,
    filter_capitalized,
    filter_gpg,
    filter_length,
    filter_regex,
    filter_signoff,
    filter_singleline,
    filter_trailing_period,
)
from dikort.print import print_error, print_success

RULES = {
    "params_section": "rules",
    "check_merge_commits": False,
    "checks": {
        "Summary length": {
            "param": "length",
            "filter": filter_length,
        },
        "Trailing period": {
            "param": "trailing_period",
            "filter": filter_trailing_period,
        },
        "Capitalized summary": {
            "param": "capitalized_summary",
            "filter": filter_capitalized,
        },
        "Signle line summary": {
            "param": "singleline_summary",
            "filter": filter_singleline,
        },
        "Signoff": {
            "param": "signoff",
            "filter": filter_signoff,
        },
        "GPG": {
            "param": "gpg",
            "filter": filter_gpg,
        },
        "Regex": {
            "param": "regex",
            "filter": filter_regex,
        },
        "Author name regex": {
            "param": "author_name_regex",
            "filter": filter_author_name_regex,
        },
        "Author email regex": {
            "param": "author_email_regex",
            "filter": filter_author_email_regex,
        },
    },
}


MERGE_RULES = {
    "params_section": "merge_rules",
    "check_merge_commits": True,
    "checks": {
        "Summary length (merge commits)": {
            "param": "length",
            "filter": filter_length,
        },
        "Trailing period (merge commits)": {
            "param": "trailing_period",
            "filter": filter_trailing_period,
        },
        "Capitalized summary (merge commits)": {
            "param": "capitalized_summary",
            "filter": filter_capitalized,
        },
        "Signle line summary (merge commits)": {
            "param": "singleline_summary",
            "filter": filter_singleline,
        },
        "Signoff (merge commits)": {
            "param": "signoff",
            "filter": filter_signoff,
        },
        "GPG (merge commits)": {
            "param": "gpg",
            "filter": filter_gpg,
        },
        "Regex (merge commits)": {
            "param": "regex",
            "filter": filter_regex,
        },
        "Author name regex (merge commits)": {
            "param": "author_name_regex",
            "filter": filter_author_name_regex,
        },
        "Author email regex (merge commits)": {
            "param": "author_email_regex",
            "filter": filter_author_email_regex,
        },
    },
}


def _generic_check(commit_range, predicate, check_merge_commits):
    desired_parents_count = 2 if check_merge_commits else 1
    try:
        return list(
            filter(
                predicate,
                filter(
                    lambda commit: len(commit.parents) == desired_parents_count,
                    commit_range,
                ),
            )
        )
    except GitCommandError as err:
        print_error(f"Cannot read commit in rage. Error: {err}")
        sys.exit(ERROR_EXIT_CODE)


def analyze_commits(config):
    logging.info("Start checks")
    repo = _open_repository(config)
    all_clear = True
    for rules in [RULES, MERGE_RULES]:
        params_section = rules["params_section"]
        for rule in rules["checks"]:
            param_name = rules["checks"][rule]["param"]
            if not config[params_section][param_name]:
                logging.info("Rule '%s' disabled. Skip.", rule)
                continue
            logging.debug("Rule '%s' enabled. Start.", rule)
            print(f"[{rule}] - ", end="")
            predicate = functools.partial(
                rules["checks"][rule]["filter"],
                config=config[f"{params_section}.settings"],
            )
            failed_commits = _generic_check(
                repo.iter_commits(rev=config["main"]["range"]),
                predicate,
                rules["check_merge_commits"],
            )
            all_clear = _process_failed_commits(all_clear, failed_commits, rule)
    _finish(all_clear)


def _open_repository(config):
    repository_path = config["main"]["repository"]
    logging.debug("Open repo at %s", repository_path)
    try:
        repo = Repo(repository_path)
    except (NoSuchPathError, InvalidGitRepositoryError) as err:
        print_error(f"Cannot open git repo at {repository_path}. Error: {err}")
        sys.exit(ERROR_EXIT_CODE)
    return repo


def _finish(all_clear):
    if all_clear:
        logging.info("All clear.")
        print_success("All clear.")
    else:
        print_error("Some checks are failed.")
        logging.info("Some checks are failed.")
        logging.info("Exit with state %d", FAILED_EXIT_CODE)
        sys.exit(FAILED_EXIT_CODE)


def _process_failed_commits(all_clear, failed_commits, rule):
    if failed_commits:
        print_error("ERROR")
        all_clear = False
        logging.info(
            "Failed %d commit for '%s' rule", len(failed_commits), rule
        )
        for commit in failed_commits:
            logging.debug(
                "Hash: %s, message: '%s'", commit.hexsha, commit.summary
            )
            print(f"Hash: {commit.hexsha}, message: '{commit.summary}'")
    else:
        logging.info("Errors not found for rule '%s'", rule)
        print_success("SUCCESS")
    return all_clear
