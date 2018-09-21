import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

from espurna_nightly_builder.errors import Error


def exc_handler(exc_type, exc_value, exc_trace):
    if issubclass(exc_type, Error):
        log.error('Exiting: "{}"'.format(exc_value))
    else:
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_trace))


sys.excepthook = exc_handler

from espurna_nightly_builder.api import Repo, Api
from espurna_nightly_builder.prepare import prepare
from espurna_nightly_builder.mkenv import mkenv
from espurna_nightly_builder.setup_repo import setup_repo
from espurna_nightly_builder.rename_releases import rename_releases, VERSION_FMT


# TODO argparse?
# TODO TRAVIS_REPO_SLUG too?
def get_env_config():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise Error("no token configured?")

    event = os.environ.get("TRAVIS_EVENT_TYPE")
    repo = os.environ.get("TRAVIS_REPO_SLUG")
    if not event or not repo:
        raise Error("not in travis?")

    return token, event, repo


TOKEN, EVENT, REPO = get_env_config()
API = Api(TOKEN)


def f_prepare(args):
    if EVENT == "cron":
        log.info("Starting nightly builder checks")
    elif EVENT == "api":
        log.error("Continuing to the next stage")
        sys.exit(0)
    else:
        log.error("Unknown travis event type")
        sys.exit(1)

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


def setup_argparse():
    parser = argparse.ArgumentParser()

    parser.add_argument("--commit-filename", default="commit.txt")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--builder-branch", default="nightly")
    parser.set_defaults(func=lambda _: parser.print_help())

    subparser = parser.add_subparsers()

    cmd_setup_repo = subparser.add_parser("setup_repo", help=setup_repo.__doc__)
    cmd_setup_repo.set_defaults(func=f_setup_repo)

    cmd_prepare = subparser.add_parser("prepare", help=prepare.__doc__)
    cmd_prepare.add_argument("target_repo")
    cmd_prepare.add_argument("builder_repo", default=REPO)
    cmd_prepare.set_defaults(func=f_prepare)

    cmd_mkenv = subparser.add_parser("mkenv", help=mkenv.__doc__)
    cmd_mkenv.add_argument("builder_repo")
    cmd_mkenv.set_defaults(func=f_mkenv)

    cmd_rename_releases = subparser.add_parser(
        "rename_releases",
        help="replace release files '{{version}}' string with '{}'".format(VERSION_FMT),
    )
    cmd_rename_releases.add_argument("releases_dir")
    cmd_rename_releases.set_defaults(func=f_rename_releases)

    return parser


def main():
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
