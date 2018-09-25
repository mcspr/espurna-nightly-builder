import logging

log = logging.getLogger(__name__)


# TODO just print this? check if env is preserved between script groups (gitlab especially)
def mkenv(
    target_repo, builder_repo, builder_branch="nightly", commit_filename="commit.txt"
):
    """Preserve github's release unique id."""

    url = target_repo.clone_url

    release = builder_repo.latest_release()
    number = release["number"]

    commit_file = builder_repo.file(builder_branch, commit_filename)
    sha = commit_file.content

    log.info("release for %s - {number:%d sha:%s}", url, number, sha)

    with open("environment", "w") as f:
        f.write("export NIGHTLY_TARGET_REPO_URL={}\n".format(url))
        f.write("export NIGHTLY_RELEASE_NUMBER={}\n".format(number))
        f.write("export NIGHTLY_COMMIT_SHA={}\n".format(sha))
