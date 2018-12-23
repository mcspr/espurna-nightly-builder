import logging

from espurna_nightly_builder import errors
from espurna_nightly_builder.api import release_is_head, CommitRange
from espurna_nightly_builder.util import nightly_tag

log = logging.getLogger(__name__)


def prepare(
    target_repo,
    builder_repo,
    target_branch="dev",
    builder_branch="nightly",
    source_directory="code/",
    commit_filename="commit.txt",
):
    """Run in install phase.
    Do series of checks to verify that target_branch HEAD commit is eligable for building.
    Commit HEAD sha value to the builder_branch and prepare release pointing to it."""
    head_sha = target_repo.branch_head(target_branch)
    log.info("head commit: {}".format(head_sha))
    if release_is_head(target_repo, head_sha):
        raise errors.TargetReleased

    state, _ = target_repo.commit_status(head_sha)
    log.info("commit state: {}".format(state))
    if state != "success":
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
    tag = nightly_tag()
    msg = "Nightly build ({})".format(tag)
    _, builder_commit = builder_repo.update_file(builder_branch, commit_file, msg)

    builder_repo.create_release(
        tag=tag,
        name=msg,
        sha=builder_commit["sha"],
        body=commit_range.html_url,
        prerelease=True,
    )
