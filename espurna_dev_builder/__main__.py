import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

from espurna_dev_builder.errors import Error

def exc_handler(exc_type, exc_value, exc_trace):
    if issubclass(exc_type, Error):
        log.error("Exiting: \"{}\"".format(exc_value))
    else:
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_trace))

sys.excepthook = exc_handler

from espurna_dev_builder.api import Repo, Api
from espurna_dev_builder.prepare import prepare
from espurna_dev_builder.mkenv import mkenv
from espurna_dev_builder.setup_repo import setup_repo
from espurna_dev_builder.rename_releases import rename_releases


# TODO argparse?
def get_env_config():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Error("no token configured?")

    event = os.environ.get("TRAVIS_EVENT_TYPE")
    if not event:
        raise Error("not in travis?")

    return token, event


TOKEN, EVENT = get_env_config()


if EVENT == "cron":
    log.info("Starting nightly builder checks")
elif EVENT == "api":
    log.error("Continuing to the next stage")
    sys.exit(0)
else:
    log.error("Unknown travis event type")
    sys.exit(1)

API = Api(TOKEN)

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers()

parser.add_argument("--commit-filename", default="commit.txt")
parser.add_argument("--target-branch", default="dev")
parser.add_argument("--builder-branch", default="nightly")


def f_prepare(args):
    target_repo = Repo(args.target_repo, api=API)
    builder_repo = Repo(args.builder_repo, api=API)
    prepare(
        target_repo,
        builder_repo,
        target_branch=args.target_branch,
        builder_branch=args.builder_branch,
        commit_filename=args.commit_filename,
    )


def f_mkenv(args):
    builder_repo = Repo(args.builder_repo, api=API)
    mkenv(builder_repo)


def f_setup_repo(args):
    setup_repo(branch=args.builder_branch, commit_filename=args.commit_filename)


def f_rename_releases(args):
    rename_releases(args.releases_dir)


cmd_prepare = subparser.add_parser("prepare")
cmd_prepare.add_argument("target_repo")
cmd_prepare.add_argument("builder_repo")
cmd_prepare.set_defaults(func=f_prepare)

cmd_mkenv = subparser.add_parser("mkenv")
cmd_mkenv.add_argument("builder_repo")
cmd_mkenv.set_defaults(func=f_mkenv)

cmd_setup_repo = subparser.add_parser("setup_repo")
cmd_setup_repo.set_defaults(func=f_setup_repo)

cmd_rename_releases = subparser.add_parser("rename_releases")
cmd_rename_releases.add_argument("releases_dir")
cmd_rename_releases.set_defaults(func=f_rename_releases)

args = parser.parse_args()
args.func(args)
