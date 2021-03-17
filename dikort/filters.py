import logging


def filter_singleline(commit, *, config):
    logging.debug("Check %s commit for singleline", commit.hexsha)
    summary_lines_count = commit.summary.count("\n")
    singleline_summary = config["singleline_summary"]
    return (summary_lines_count > 1 and singleline_summary) or (  # noqa: WPS408
        summary_lines_count == 1 and not singleline_summary
    )


def filter_trailing_period(commit, *, config):
    logging.debug("Check %s commit for trailing period", commit.hexsha)
    summary = commit.summary
    return summary.endswith(".") != config["trailing_period"]


def filter_capitalized(commit, *, config):
    logging.debug("Check %s commit for capitalized subject", commit.hexsha)
    summary_first_letter = commit.summary[0]
    return summary_first_letter.isalpha() and summary_first_letter.isupper() != config["capitalized_summary"]


def filter_length(commit, *, config):
    logging.debug("Check %s commit for summary message length", commit.hexsha)
    min_length = config["min_length"]
    max_length = config["max_length"]
    length = len(commit.summary)
    return length < min_length or length > max_length


def filter_signoff(commit, *, config):
    last_msg_line = commit.message.rstrip().split("\n")[-1]
    return last_msg_line.startswith("Signed-off-by") != config["signoff"]


def filter_gpg(commit, *, config):
    logging.debug("Check %s commit for GPG sign", commit.hexsha)
    return bool(commit.gpgsig) != config["gpg"]


def filter_regex(commit, *, config):
    logging.debug("Check %s commit for regex", commit.hexsha)
    return not config["regex"].match(commit.summary)


def filter_author_name_regex(commit, *, config):
    logging.debug("Check %s commit for author name", commit.hexsha)
    return not config["author_name_regex"].match(commit.author.name)


def filter_author_email_regex(commit, *, config):
    logging.debug("Check %s commit for author email", commit.hexsha)
    return not config["author_email_regex"].match(commit.author.email)
