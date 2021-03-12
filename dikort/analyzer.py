import sys

from git import Repo

from dikort.print import print_error, print_success


def _check_singleline(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
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
            failed.append(commit)
    return failed


def _check_trailing_period(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        summary = commit.summary
        if summary.endswith(".") != config["rules.settings"].getboolean(
            "trailing-period"
        ):
            failed.append(commit)
    return failed


def _check_capitalized(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        summary = commit.summary
        if summary.isalpha() and summary.isupper() == config[
            "rules.settings"
        ].getboolean("capitalized-summary"):
            failed.append(commit)
    return failed


def _check_length(commit_range, config):
    failed = []
    min_length = config["rules.settings"].getint("min-length")
    max_length = config["rules.settings"].getint("max-length")
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        length = len(commit.summary)
        if length < min_length or length > max_length:
            failed.append(commit)
    return failed


def _check_signoff(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        last_msg_line = commit.message.rstrip().split('\n')[-1]
        if last_msg_line.startswith("Signed-off-by") != config[
            "rules.settings"
        ].getboolean("signoff"):
            failed.append(commit)
    return failed


RULES = {
    "Summary length": {
        "param": "length",
        "checker": _check_length,
    },
    "Trailing period": {
        "param": "trailing-period",
        "checker": _check_trailing_period,
    },
    "Capitalized summary": {
        "param": "capitalized-summary",
        "checker": _check_capitalized,
    },
    "Signle line summary": {
        "param": "singleline-summary",
        "checker": _check_singleline,
    },
    "Signoff": {
        "param": "signoff",
        "checker": _check_signoff,
    },
}


def check(config):
    repo = Repo(config["main"]["repository"])
    all_clear = True
    for rule in RULES:
        if not config["rules"].getboolean(RULES[rule]["param"]):
            continue
        print(f"[{rule}] - ", end="")
        failed = RULES[rule]["checker"](
            repo.iter_commits(rev=config["main"]["range"]), config
        )
        if failed:
            print_error("ERROR")
            all_clear = False
            for commit in failed:
                print(f"Hash: {commit.hexsha}, summary: {commit.summary}")
        else:
            print_success("SUCCESS")
    if all_clear:
        print_success("All clear.")
    else:
        print_error("Some checks are failed.")
        sys.exit(1)
