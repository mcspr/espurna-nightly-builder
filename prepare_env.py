#!/usr/bin/env python
import os
import json
import time
import sys
import subprocess

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests


def c_print(msg):
    print('\x1b[0;33m{}\x1b[0m'.format(msg))


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


def get_latest_release_commit(token, endpoint="https://api.github.com/graphql"):
    query = """
    query {
        repository(owner:\"mcspr\", name:\"espurna-travis-test\") {
            releases(last:1) {
                nodes {
                    publishedAt
                    description
                    resourcePath
                }
            }
        }
    }""".strip()
    query = json.dumps({"query": query})

    headers = {
        "Authorization": "token {}".format(token),
        "User-Agent": "mcspr/espurna-travis-test/builder-v1.0"
    }

    result = requests.post(endpoint,headers=headers, data=query)
    result = result.json()

    (release, ) = result["data"]["repository"]["releases"]["nodes"]

    url = urljoin("https://github.com", release["resourcePath"])

    c_print(">>> Latest release <<<\n"
    "url: https://github.com/{resourcePath}\n"
    "date: {publishedAt}\n"
    "description: {description}".format(**release))

    if not release["description"]:
        return None

    return release["description"].split("/")[-1]


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
        c_print("Skipping normal release")
        write_env_and_exit(None, False)

    release_commit = get_latest_release_commit(os.environ["GITHUB_TOKEN"])
    if not release_commit:
        c_print("No commit bound to the previous build")
        write_env_and_exit(None, False)

    if commits["dev"] == release_commit:
        c_print("Skipping already released commit")
        write_env_and_exit(None, False)

    write_env_and_exit(commits["dev"], True)
