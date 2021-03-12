import functools
import logging
import re
import sys

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from dikort.config import ERROR_EXIT_CODE, FAILED_EXIT_CODE
from dikort.print import print_error, print_success


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


def _filter_singleline(commit, *, config):
    logging.debug("Check %s commit for singleline", commit.hexsha)
    summary_lines_count = commit.summary.count("\n")
    singleline_summary = config["rules.settings"].getboolean(
        "singleline-summary"
    )
    if (
        summary_lines_count > 1
        and singleline_summary
        or summary_lines_count == 1
        and not singleline_summary
    ):
        return True
    return False


def _filter_trailing_period(commit, *, config):
    logging.debug("Check %s commit for trailing period", commit.hexsha)
    summary = commit.summary
    if summary.endswith(".") != config["rules.settings"].getboolean(
        "trailing-period"
    ):
        return True
    return False


def _filter_capitalized(commit, *, config):
    logging.debug("Check %s commit for capitalized subject", commit.hexsha)
    summary = commit.summary
    if summary.isalpha() and summary.isupper() == config[
        "rules.settings"
    ].getboolean("capitalized-summary"):
        return True
    return False


def _filter_length(commit, *, config):
    logging.debug("Check %s commit for summary message length", commit.hexsha)
    min_length = config["rules.settings"].getint("min-length")
    max_length = config["rules.settings"].getint("max-length")
    length = len(commit.summary)
    if length < min_length or length > max_length:
        return True
    return False


def _filter_signoff(commit, *, config):
    last_msg_line = commit.message.rstrip().split("\n")[-1]
    if last_msg_line.startswith("Signed-off-by") != config[
        "rules.settings"
    ].getboolean("signoff"):
        return True
    return False


def _filter_gpg(commit, *, config):
    logging.debug("Check %s commit for GPG sign", commit.hexsha)
    if bool(commit.gpgsig) != config["rules.settings"].getboolean("gpg"):
        return True
    return False


def _filter_regex(commit, *, config):
    logging.debug("Check %s commit for regex", commit.hexsha)
    regex = re.compile(config["rules.settings"].get("regex"))
    if not regex.match(commit.summary):
        return True
    return False


def _filter_author_name_regex(commit, *, config):
    logging.debug("Check %s commit for author name", commit.hexsha)
    regex = re.compile(config["rules.settings"].get("author-name-regex"))
    if not regex.match(commit.author.name):
        return True
    return False


def _filter_author_email_regex(commit, *, config):
    logging.debug("Check %s commit for author email", commit.hexsha)
    regex = re.compile(config["rules.settings"].get("author-email-regex"))
    if not regex.match(commit.author.email):
        return True
    return False


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


def check(config):
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
