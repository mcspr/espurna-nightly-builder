import argparse
import logging
import os
import sys


from .errors import Error
from .api import Repo, Api
from .prepare import prepare
from .mkenv import mkenv
from .setup_repo import setup_repo
from .rename_releases import rename_releases
from .util import nightly_tag, last_month_prefix


logging.basicConfig(
    level=logging.INFO, format="%(relativeCreated)6d %(levelname)-8s %(message)s"
)
log = logging.getLogger("main")


def exc_handler(exc_type, exc_value, exc_trace):
    if issubclass(exc_type, errors.Error):
        log.error('Exiting: "{}"'.format(exc_value))
    else:
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_trace))


sys.excepthook = exc_handler


# TODO argparse?
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
VERSION_FMT = "{orig_version}.nightly{tag}+git{sha:.8}"


def f_prepare(args):
    if EVENT == "cron":
        log.info("Starting nightly builder checks")
    elif EVENT == "api":
        log.info("Continuing to the next stage")
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
        source_directory=args.source_directory,
        commit_filename=args.commit_filename,
    )


def f_mkenv(args):
    target_repo = Repo(args.target_repo, api=API)
    builder_repo = Repo(args.builder_repo, api=API)
    mkenv(
        target_repo,
        builder_repo,
        builder_branch=args.builder_branch,
        commit_filename=args.commit_filename,
    )


def f_setup_repo(args):
    setup_repo(branch=args.builder_branch, commit_filename=args.commit_filename)


def f_rename_releases(args):
    rename_releases(
        releases_dir=args.releases_dir,
        version_template=args.version,
        tag=nightly_tag(),
        sha=args.sha,
    )


def f_list_tags(args):
    builder_repo = Repo(args.builder_repo, api=API)

    tags = builder_repo.tags()
    log.info("tags:\n%s", "\n".join([tag["name"] for tag in tags]))


def f_delete_releases(args):
    builder_repo = Repo(args.builder_repo, api=API)

    prefix = args.prefix

    tags = builder_repo.tags()

    releases = builder_repo.releases(last=len(tags))
    releases = [
        release
        for release in releases
        if (release["tagName"] and release["tagName"].startswith(prefix))
        or "untagged" in release["url"]
    ]

    for release in releases:
        log.info("tagName:%(tagName)s number:%(number)d", release)
        if builder_repo.delete_release(release["number"]):
            log.info("deleted release")
        else:
            log.error("could not delete the release")
        if builder_repo.delete_tag(release["tagName"]):
            log.info("deleted tag")
        else:
            log.error("could not delete the tag")


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
    cmd_prepare.add_argument("--source-directory", default="code/")
    cmd_prepare.add_argument("target_repo")
    cmd_prepare.add_argument("builder_repo", nargs="?", default=REPO)
    cmd_prepare.set_defaults(func=f_prepare)

    cmd_mkenv = subparser.add_parser("mkenv", help=mkenv.__doc__)
    cmd_mkenv.add_argument("target_repo")
    cmd_mkenv.add_argument("builder_repo", nargs="?", default=REPO)
    cmd_mkenv.set_defaults(func=f_mkenv)

    cmd_rename_releases = subparser.add_parser(
        "rename_releases",
        help="format release files '{{version}}' string with '--version' value",
    )
    cmd_rename_releases.add_argument("--sha")
    cmd_rename_releases.add_argument("--version", default=VERSION_FMT)
    cmd_rename_releases.add_argument("releases_dir")
    cmd_rename_releases.set_defaults(func=f_rename_releases)

    cmd_list_tags = subparser.add_parser("list_tags")
    cmd_list_tags.add_argument("builder_repo", nargs="?", default=REPO)
    cmd_list_tags.set_defaults(func=f_list_tags)

    cmd_list_tags = subparser.add_parser("delete_releases")
    cmd_list_tags.add_argument("--prefix", default=last_month_prefix())
    cmd_list_tags.add_argument("builder_repo", nargs="?", default=REPO)
    cmd_list_tags.set_defaults(func=f_delete_releases)

    return parser


def main():
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
