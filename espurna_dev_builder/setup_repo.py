import os
import subprocess

def setup_repo(cfilename="commit.txt"):
    origin_url = subprocess.check_output(["git", "remote", "get-url", "origin"]).strip()

    os.mkdir('nightly')
    os.chdir('nightly')
    with open(cfilename, "w") as f:
        f.write("-")

    subprocess.call(["git", "init"])
    subprocess.call(["git", "remote", "add", "origin", origin_url])
    subprocess.call(["git", "add", cfilename])
    subprocess.call(["git", "commit", "-m", "initial commit"])
    subprocess.call(["git", "push", "-u", "origin"])


