import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("main")

from espurna_dev_builder.api import Repo, Api
from espurna_dev_builder.prepare import prepare
from espurna_dev_builder.mkenv import mkenv
from espurna_dev_builder.errors import Error


# TODO argparse?
def get_env_config():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("no token configured?")

    event = os.environ.get("TRAVIS_EVENT_TYPE")
    if not event:
        raise ValueError("not in travis?")

    return token, event


TOKEN, EVENT = get_env_config()


if EVENT == "cron":
    log.info("Starting nightly builder checks")
elif EVENT == "api":
    log.error("Continuing to the next stage")
    sys.exit(0)
else:
    log.error("Unknown travis event type")
    sys.exit(1)

API = Api(TOKEN)

target_repo = Repo("xoseperez/espurna", api=API)
builder_repo = Repo("mcspr/espurna-travis-test", api=API)

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["prepare", "mkenv"])
args = parser.parse_args()


if args.mode == "prepare":
    prepare(target_repo, builder_repo, target_branch="dev", builder_branch="nightly")
elif args.mode == "mkenv":
    mkenv(builder_repo)
