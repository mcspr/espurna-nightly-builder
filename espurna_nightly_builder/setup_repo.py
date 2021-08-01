import os
import subprocess


def setup_repo(branch, commit_filename):
    """Initial setup for builder_branch. Required to run once before running prepare / check_release."""
    origin_url = subprocess.check_output(["git", "remote", "get-url", "origin"]).strip()

    os.mkdir(branch)
    os.chdir(branch)
    with open(commit_filename, "w") as f:
        f.write("-")

    subprocess.call(["git", "init"])
    subprocess.call(["git", "remote", "add", "origin", origin_url])
    subprocess.call(["git", "checkout", "-b", branch])
    subprocess.call(["git", "add", commit_filename])
    subprocess.call(["git", "commit", "-m", "initial commit"])
    subprocess.call(["git", "push", "-u", "origin", branch])


class SetupRepo:
    command = "setup-repo"
    __doc__ = setup_repo.__doc__

    def __init__(self, parser):
        pass

    def __call__(self, args):
        setup_repo(branch=args.builder_branch, commit_filename=args.commit_filename)
