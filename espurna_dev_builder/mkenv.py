import logging

log = logging.getLogger(__name__)


def mkenv(repo):
    release = repo.latest_release()
    number = release["number"]
    log.info("exporting release number: {}".format(number))
    with open("environment", "w") as f:
        f.write("export TRAVIS_RELEASE_NUMBER={}\n".format(number))
