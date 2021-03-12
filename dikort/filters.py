import logging
import re


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