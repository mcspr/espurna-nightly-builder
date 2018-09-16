import os
import subprocess


def setup_repo(branch, commit_filename):
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
