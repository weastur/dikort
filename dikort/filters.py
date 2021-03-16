import logging


def filter_singleline(commit, *, config):
    logging.debug("Check %s commit for singleline", commit.hexsha)
    summary_lines_count = commit.summary.count("\n")
    singleline_summary = config["singleline_summary"]
    if (
        summary_lines_count > 1
        and singleline_summary
        or summary_lines_count == 1
        and not singleline_summary
    ):
        return True
    return False


def filter_trailing_period(commit, *, config):
    logging.debug("Check %s commit for trailing period", commit.hexsha)
    summary = commit.summary
    if summary.endswith(".") != config["trailing_period"]:
        return True
    return False


def filter_capitalized(commit, *, config):
    logging.debug("Check %s commit for capitalized subject", commit.hexsha)
    summary_first_letter = commit.summary[0]
    if (
        summary_first_letter.isalpha()
        and summary_first_letter.isupper() != config["capitalized_summary"]
    ):
        return True
    return False


def filter_length(commit, *, config):
    logging.debug("Check %s commit for summary message length", commit.hexsha)
    min_length = config["min_length"]
    max_length = config["max_length"]
    length = len(commit.summary)
    if length < min_length or length > max_length:
        return True
    return False


def filter_signoff(commit, *, config):
    last_msg_line = commit.message.rstrip().split("\n")[-1]
    if last_msg_line.startswith("Signed-off-by") != config["signoff"]:
        return True
    return False


def filter_gpg(commit, *, config):
    logging.debug("Check %s commit for GPG sign", commit.hexsha)
    if bool(commit.gpgsig) != config["gpg"]:
        return True
    return False


def filter_regex(commit, *, config):
    logging.debug("Check %s commit for regex", commit.hexsha)
    if not config["regex"].match(commit.summary):
        return True
    return False


def filter_author_name_regex(commit, *, config):
    logging.debug("Check %s commit for author name", commit.hexsha)
    if not config["author_name_regex"].match(commit.author.name):
        return True
    return False


def filter_author_email_regex(commit, *, config):
    logging.debug("Check %s commit for author email", commit.hexsha)
    if not config["author_email_regex"].match(commit.author.email):
        return True
    return False
