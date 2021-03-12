from git import Repo


def check(config):
    repo = Repo(config["main"]["repository"])
    for commit in repo.iter_commits(rev=config["main"]["range"]):
        print(commit)