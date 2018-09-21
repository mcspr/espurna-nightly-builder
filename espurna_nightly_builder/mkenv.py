import logging

log = logging.getLogger(__name__)


# TODO just print this? check if env is preserved between script groups (gitlab especially)
def mkenv(repo):
    """Preserve github's release unique id."""
    release = repo.latest_release()
    number = release["number"]
    log.info("exporting release number: {}".format(number))
    with open("environment", "w") as f:
        f.write("export TRAVIS_RELEASE_NUMBER={}\n".format(number))
