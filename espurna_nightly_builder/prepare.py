import logging

from . import errors
from .api import release_is_head, CommitRange
from .util import nightly_tag

log = logging.getLogger(__name__)


def prepare(
    target_repo,
    builder_repo,
    target_branch="dev",
    builder_branch="nightly",
    source_directory="code/",
    commit_filename="commit.txt",
):
    """Expected to be called periodically.
    Do series of checks to verify that target_branch HEAD commit is eligable for building.
    Commit HEAD sha value to the builder_branch and create a lightweight tag pointing to it."""

    head = target_repo.branches(target_branch)
    head_sha = head["commit"]["sha"]

    log.info("head commit: {}".format(head_sha))
    if release_is_head(target_repo, head_sha):
        raise errors.TargetReleased

    count, check_runs = target_repo.commit_check_runs(head_sha)
    if not count:
        raise errors.NoChecks

    for run in check_runs:
        if (run["status"] != "completed") or (run["conclusion"] != "success"):
            raise errors.Unbuildable

    commit_file = builder_repo.file(builder_branch, commit_filename)
    if not commit_file.content:
        raise errors.NoContent

    old_sha = commit_file.content

    log.info("latest nightly: {}".format(old_sha))
    if old_sha == head_sha:
        raise errors.Released

    commit_range = CommitRange(target_repo, old_sha, head_sha)
    if not commit_range.path_changed(source_directory):
        raise errors.NotChanged

    commit_file.content = head_sha
    response = builder_repo.update_file(
        builder_branch, commit_file, "Nightly build ({})".format(nightly_tag())
    )
    log.info(
        "updated commit.txt, new nightly branch commit: {}".format(
            response["commit"]["sha"]
        )
    )


class Prepare:
    command = "prepare"
    __doc__ = prepare.__doc__

    @staticmethod
    def setup(parser):
        parser.add_argument("--source-directory", default="code/")
        parser.add_argument("target_repo")
        parser.add_argument("builder_repo")

    @staticmethod
    def function(args):
        target_repo = Repo(args.target_repo, api=api_client(args))
        builder_repo = Repo(args.builder_repo, api=api_client(args))
        prepare(
            target_repo,
            builder_repo,
            target_branch=args.target_branch,
            builder_branch=args.builder_branch,
            source_directory=args.source_directory,
            commit_filename=args.commit_filename,
        )
