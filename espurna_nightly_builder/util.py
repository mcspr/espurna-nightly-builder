import sys
import time
import datetime
from subprocess import check_output


from .api import Repo, Api


def run(cmd, cwd=None):
    out = check_output(cmd, cwd=cwd)
    out = out.decode(sys.getfilesystemencoding()).strip()

    return out


def nightly_tag():
    return time.strftime("%Y%m%d")


def git_head(short=False, cwd=None):
    cmd = ["git", "rev-parse", "HEAD"]
    if short:
        cmd.insert(-1, "--short")
    return run(cmd=cmd, cwd=cwd)


def last_month_prefix():
    date = datetime.datetime.utcnow()
    delta = datetime.timedelta(1)
    last = date.replace(day=1) - delta

    return last.strftime("%Y%m")


# helpers to generate Repo object
def builder_repo_from_args(args):
    return Repo(args.builder_repo, api=Api(args.token))


def target_repo_from_args(args):
    return Repo(args.target_repo, api=Api(args.token))


def repos_from_args(args):
    return [target_repo_from_args(args), builder_repo_from_args(args)]
