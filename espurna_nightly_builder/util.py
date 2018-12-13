import sys
import time
import datetime
from subprocess import check_output


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


def compare_url(repo, start, end):
    url = "https://github.com/{owner}/{name}/compare/{start}...{end}".format(
        owner=repo.owner, name=repo.name, start=start, end=end
    )
    return url


def last_month_prefix():
    date = datetime.datetime.utcnow()
    delta = datetime.timedelta(1)
    last = date.replace(day=1) - delta

    return last.strftime("%Y%m")
