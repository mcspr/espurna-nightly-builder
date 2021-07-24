import argparse
import logging
import os
import sys


from . import errors
from .api import Repo, Api, CommitRange
from .prepare import Prepare
from .setup_repo import SetupRepo
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


def api_client(args):
    if not hasattr(api_client, "instance"):
        api_client.instance = Api(args.token)

    return api_client.instance
    subparser = parser.add_subparsers()


class Workflow:
    """
    Queue the specified workflow_id
    """

    command = "workflow"

    @staticmethod
    def setup(parser):
        parser.add_argument("--id", required=True)
        parser.add_argument("--ref", required=True)
        parser.add_argument("target_repo")
        parser.add_argument("builder_repo")

    @staticmethod
    def function(args):
        builder_repo = Repo(args.builder_repo, api=api_client(args))
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

    @staticmethod
    def setup(parser):
        parser.add_argument("builder_repo")

    @staticmethod
    def function(args):
        builder_repo = Repo(args.builder_repo, api=api_client(args))
        for tag in builder_repo.tags():
            log.info("%s", tag["name"])


class ListReleases:
    command = "list-releases"

    @staticmethod
    def setup(parser):
        parser.add_argument("--last", type=int, default=1)
        parser.add_argument("builder_repo")

    @staticmethod
    def function(args):
        builder_repo = Repo(args.builder_repo, api=api_client(args))
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

    @staticmethod
    def setup(parser):
        parser.add_argument("--prefix", default=last_month_prefix())
        parser.add_argument("builder_repo")

    @staticmethod
    def function(args):
        builder_repo = Repo(args.builder_repo, api=api_client(args))
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

    @staticmethod
    def function(args):
        builder_repo = Repo(args.builder_repo, api=api_client(args))

        head = builder_repo.branches(args.builder_branch)
        sha = head["commit"]["sha"]
        message = head["commit"]["commit"]["message"]
        log.info("builder head:%s message:%s", sha, message)

        target_commit = builder_repo.file(sha, args.commit_filename).content
        log.info("head target:%s", target_commit)

    @staticmethod
    def setup(parser):
        parser.add_argument("builder_repo")


def setup_parser_handlers(parser, handlers):
    for handler in handlers:
        handler_parser = parser.add_parser(
            handler.command, help=handler.__doc__ or None
        )

        setup = getattr(handler, "setup", None)
        if setup:
            setup(handler_parser)

        handler_parser.set_defaults(func=handler.function)


def setup_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--commit-filename", default="commit.txt")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--builder-branch", default="nightly")
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
