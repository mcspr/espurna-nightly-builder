#!/usr/bin/env python2
import argparse
import sys
import os
import itertools
from collections import OrderedDict
from ConfigParser import ConfigParser

from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

import ruamel
from ruamel.yaml import YAML

yaml = YAML()
yaml.block_seq_indent = 2
yaml.default_flow_style = False
yaml.errors = "strict"
yaml.indent(offset=2, sequence=4)
ruamel.yaml.representer.RoundTripRepresenter.add_representer(
    OrderedDict, ruamel.yaml.representer.RoundTripRepresenter.represent_dict
)


def build_obj(env):
    obj = OrderedDict()

    obj["stage"] = "build"
    obj["dependencies"] = ["prepare:platformio"]
    obj["only"] = ["tags"]

    obj["artifacts"] = {"expire_in": "1h", "paths": ["espurna/firmware"]}
    obj["script"] = [
        ". venv/bin/activate",
        "cd espurna/code && ./build.sh {ENV}".format(ENV=env),
    ]

    return {"build:{ENV}".format(ENV=env): obj}


def package_obj(deps):
    obj = OrderedDict()

    obj["stage"] = "package"
    obj["dependencies"] = deps
    obj["artifacts"] = {"expire_in": "1h", "paths": ["release.tar.xz"]}
    obj["script"] = ["find espurna/firmware", "tar cJf release.tar.xz espurna/firmware"]
    obj["only"] = ["tags"]

    return {"package:release-txz": obj}


def get_environments(platformio_ini="espurna/code/platformio.ini"):
    cfg = ConfigParser()
    cfg.read(platformio_ini)

    for section in cfg.sections():
        if not section.startswith("env:"):
            continue
        if section.endswith("-ota"):
            continue
        if "travis" in section:
            continue

        _, _, env = section.partition(":")

        yield env


def gitlab_ci_yml():
    deps = []

    for env in get_environments():
        yaml.dump(build_obj(env), sys.stdout)
        sys.stdout.write("\n")
        deps.append("build:{}".format(env))

    yaml.dump(package_obj(deps), sys.stdout)

    sys.exit()


def travis_yml():
    script = "./build.sh {}"
    envs = get_environments()

    yaml.dump([{"stage": "release", "script": script.format(next(envs))}], sys.stdout)
    for env in envs:
        yaml.dump([{"script": script.format(env)}], sys.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", action="store", choices=("travis", "gitlab"))
    args = parser.parse_args()

    ({"travis": travis_yml, "gitlab": gitlab_ci_yml})[args.target]()
