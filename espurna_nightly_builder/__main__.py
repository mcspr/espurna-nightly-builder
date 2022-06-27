import argparse
import logging
import os
import sys


from . import __version__
from . import errors
from .prepare import Prepare
from .setup_repo import SetupRepo
from .util import last_month_prefix, builder_repo_from_args


logging.basicConfig(
    level=logging.INFO, format="%(relativeCreated)6d %(levelname)-8s %(message)s"
)
log = logging.getLogger("main")


def exc_handler(exc_type, exc_value, exc_trace):
    if issubclass(exc_type, errors.Error):
        log.error('Exiting: "%s"', exc_value)
    else:
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_trace))


sys.excepthook = exc_handler


class Workflow:
    """
    Queue the specified workflow_id
    """

    command = "workflow"

    def __init__(self, parser):
        parser.add_argument("--id", required=True)
        parser.add_argument("--ref", required=True)
        parser.add_argument("target_repo")
        parser.add_argument("builder_repo")

    def __call__(self, args):
        builder_repo = builder_repo_from_args(args)
        builder_repo.workflow_dispatch(
            workflow_id=args.id, ref=args.ref, inputs={"target_repo": args.target_repo}
        )
        log.info(
            "dispatched workflow:%s for ref:%s input target_repo:%s",
            args.id,
            args.ref,
            args.target_repo,
        )


class ListTags:
    command = "list-tags"

    def __init__(self, parser):
        parser.add_argument("builder_repo")

    def __call__(self, args):
        builder_repo = builder_repo_from_args(args)
        for tag in builder_repo.tags():
            log.info("%s", tag["name"])


class ListReleases:
    command = "list-releases"

    def __init__(self, parser):
        parser.add_argument("--last", type=int, default=1)
        parser.add_argument("builder_repo")

    def __call__(self, args):
        builder_repo = builder_repo_from_args(args)
        for release in builder_repo.releases(args.last):
            log.info(
                "%s number:%d tag:%s sha:%s",
                release["publishedAt"],
                release["number"],
                release["tagName"],
                release["sha"],
            )


class DeleteReleases:
    command = "delete-releases"

    def __init__(self, parser):
        parser.add_argument("--prefix", default=last_month_prefix())
        parser.add_argument("builder_repo")

    def __call__(self, args):
        builder_repo = builder_repo_from_args(args)
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


class ShowLatest:
    command = "show-latest"

    def __init__(self, parser):
        parser.add_argument("builder_repo")

    def __call__(self, args):
        builder_repo = builder_repo_from_args(args)

        head = builder_repo.branches(args.builder_branch)
        sha = head["commit"]["sha"]
        message = head["commit"]["commit"]["message"]
        log.info("builder head:%s message:%s", sha, message)

        target_commit = builder_repo.file(sha, args.commit_filename).content
        log.info("head target:%s", target_commit)


def setup_parser_handlers(root_parser, handlers):
    for handler in handlers:
        parser = root_parser.add_parser(handler.command, help=handler.__doc__ or None)
        parser.set_defaults(func=handler(parser))


def setup_argparse():
    parser = argparse.ArgumentParser()
    parser.prog = __package__
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--commit-filename", default="commit.txt")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--builder-branch", default="nightly")
    parser.add_argument("--version", action="version", version=f"{__package__} {__version__}")
    parser.set_defaults(func=lambda _: parser.print_help())

    setup_parser_handlers(
        parser.add_subparsers(),
        (
            SetupRepo,
            Prepare,
            Workflow,
            ListTags,
            ListReleases,
            DeleteReleases,
            ShowLatest,
        ),
    )

    return parser


def main():
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
