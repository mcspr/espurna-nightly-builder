import time
import logging

from espurna_dev_builder import errors
from espurna_dev_builder.api import release_is_head

log = logging.getLogger(__name__)

def prepare(target_repo, builder_repo, target_branch="dev", builder_branch="nightly", cfilename="commit.txt"):
    head_sha = target_repo.branch_head(target_branch)
    log.info("head commit: {}".format(head_sha))
    if release_is_head(target_repo, head_sha):
        raise errors.TargetReleased

    state, _ = target_repo.commit_status(head_sha)
    log.info("commit state: {}".format(state))
    if state != "success":
        raise errors.Unbuildable

    commit_file = builder_repo.file(builder_branch, cfilename)
    if not commit_file.content:
        raise errors.NoContent

    old_sha = commit_file.content

    log.info("latest nightly: {}".format(old_sha))
    if old_sha == head_sha:
        raise errors.Released

    commit_file.content = head_sha
    msg = "nightly build / {}".format(tag)
    _, builder_commit = builder_repo.update_file(builder_branch, commit_file, msg)

    builder_repo.release(
        time.strftime("%Y%m%d"),
        builder_commit["sha"],
        target_repo.compare_url(old_sha, head_sha),
    )
