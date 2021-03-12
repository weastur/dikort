import sys

from git import Repo

from dikort.print import print_error, print_success


def _check_singleline(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        summary_lines_count = commit.summary.count("\n")
        if summary_lines_count > 1:
            failed.append(commit)
    return failed


def _check_trailing_period(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        summary = commit.summary
        if summary.isalpha() and summary.isupper():
            failed.append(commit)
    return failed


def _check_capitalized(commit_range, config):
    failed = []
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        summary = commit.summary
        if summary.isalpha() and summary.isupper():
            failed.append(commit)
    return failed


def _check_length(commit_range, config):
    failed = []
    min_length = config["rules"].getint("min-length")
    max_length = config["rules"].getint("max-length")
    for commit in commit_range:
        if len(commit.parents) > 1:
            continue
        length = len(commit.summary)
        if length < min_length or length > max_length:
            failed.append(commit)
    return failed


RULES = {
    "Summary length": _check_length,
    "Trailing period": _check_trailing_period,
    "Capitalized summary": _check_capitalized,
    "Signle line summary": _check_singleline,
}


def check(config):
    repo = Repo(config["main"]["repository"])
    all_clear = True
    for rule in RULES:
        print(f"[{rule}] - ", end="")
        failed = RULES[rule](
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
