import sys

from git import Repo

from dikort.print import print_error, print_success


def _check_length(commit, min_length, max_length):
    length = len(commit.summary)
    if length < min_length or length > max_length:
        print_error(
            f"Commit({commit.hexsha}) summary length must be [{min_length}..{max_length}]. Current: {length}. "
        )
        return False
    return True


def check(config):
    repo = Repo(config["main"]["repository"])
    all_checks_result = []
    for commit in repo.iter_commits(rev=config["main"]["range"]):
        all_checks_result.append(
            _check_length(
                commit,
                config["rules"].getint("min-length"),
                config["rules"].getint("max-length"),
            )
        )
    if all(all_checks_result):
        print_success("All clear.")
    else:
        print_error("Some checks are failed.")
        sys.exit(1)
