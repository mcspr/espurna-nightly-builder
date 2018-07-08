#!/usr/bin/env python
import os
import time
import sys
import subprocess

import requests


def get_heads(branches, cwd="espurna"):
    cmd = ["git", "ls-remote", "--heads", "origin"]
    for branch in branches:
        cmd.append("refs/heads/{}".format(branch))

    output = subprocess.check_output(cmd, cwd=cwd)
    output = output.decode("utf-8")

    commits = {}
    lines = output.split("\n")
    for line in lines:
        if not line:
            continue
        commit, ref = line.split("\t")
        commits[ref.split("/")[-1]] = commit

    return commits


def get_latest_release_body(endpoint="https://api.github.com/repos/mcspr/espurna-travis-test/releases/latest"):
    data = requests.get(endpoint).json()
    print("> Latest release:")
    print("html_url: {}".format(data["html_url"]))
    print("api_url: {}".format(data["url"]))
    return data["body"]


def write_env_and_exit(commit, do_release, filename="environment"):
    with open(filename, "w") as env:
        if commit:
            env.write("export ESPURNA_COMMIT={}\n".format(commit))
            env.write("export ESPURNA_RELEASE_TAG={}\n".format(time.strftime("%Y%m%d")))
            env.write("export ESPURNA_RELEASE_BODY=\"https://github.com/xoseperez/espurna/commit/{}\"\n".format(commit))
        env.write("export ESPURNA_DO_RELEASE={}\n".format(do_release))
    sys.exit(0)


if __name__ == "__main__":
    commits = get_heads(["dev", "master"])
    if commits["dev"] == commits["master"]:
        # Skip official build
        write_env_and_exit(None, False)

    release_body = get_latest_release_body()
    if not release_body:
        # Something is wrong with this builder?
        write_env_and_exit(None, False)

    release_commit = release_body.split("/")[-1]
    if commits["dev"] == release_commit:
        # Skipping already released commit
        write_env_and_exit(None, False)

    write_env_and_exit(commits["dev"], True)
