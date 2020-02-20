import logging

log = logging.getLogger(__name__)


# TODO just print this? check if env is preserved between script groups (gitlab especially)
def mkenv(
    target_repo, builder_repo, builder_branch="nightly", commit_filename="commit.txt"
):
    """Preserve github's release unique id."""

    target_url = target_repo.clone_url

    release = builder_repo.latest_release()

    commit_file = builder_repo.file(builder_branch, commit_filename)
    target_sha = commit_file.content

    log.info(
        "release for %s - {number:%d builder_sha:%s target_sha:%s}",
        target_url,
        release["number"],
        release["sha"],
        target_sha,
    )

    with open("environment", "w") as f:
        f.write("export NIGHTLY_TARGET_REPO_URL={}\n".format(target_url))
        f.write("export NIGHTLY_TARGET_COMMIT_SHA={}\n".format(target_sha))
        f.write("export NIGHTLY_BUILDER_RELEASE_NUMBER={}\n".format(release["number"]))
        f.write("export NIGHTLY_BUILDER_COMMIT_SHA={}\n".format(release["sha"]))
