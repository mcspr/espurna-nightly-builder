#!/usr/bin/env python2
#
# (c) 2018 Max Prokhorov, Lazar Obradovic
#
# Install PlatformIO and necessary frameworks, platforms and libs.

from ConfigParser import ConfigParser

import os
import sys
import shutil
import subprocess
import tempfile

INO = "void setup(){}\nvoid loop(){}\n"


def get_pio_libraries(cwd, platformio_ini="platformio.ini"):
    path = os.path.join(cwd, platformio_ini)

    parser = ConfigParser()
    parser.read(path)

    libs = parser.get("common", "lib_deps").split("\n")[1:]

    return libs


def pio_prepare(cwd, libraries, platforms):
    def run(exit_code):
        def wrapper(cmd):
            code = 1

            try:
                code = subprocess.call(cmd, cwd=cwd)
            except OSError as e:
                print(e, ' '.join(cmd))

            return (code == 0)

        return wrapper

    def after(path):
        def wrapper(_):
            shutil.rmtree(path)
            return True
        return wrapper

    # - explicitly install required libraries so each job has lib dependencies ready
    # - run dummy project to test compiler and install tool-scons
    commands = [
            [run(0), ["platformio", "lib", "install", "-s"] + libraries],
            [run(0), ["npm", "install", "--only=dev"]],
            [run(0), ["node", "node_modules/gulp/bin/gulp.js"]]
    ]
    for platform in platforms:
        tmpdir = tempfile.mkdtemp()

        srcdir = os.path.join(tmpdir, "src")
        os.mkdir(srcdir)
        with open(os.path.join(srcdir, "dummy.ino"), "w") as f:
            f.write(INO)

        commands.extend(
            [
                [
                    run(0),
                    [
                        "platformio",
                        "init",
                        "-d", tmpdir,
                        "-b", "esp01_1m",
                        "-O", "platform={}".format(platform),
                    ],
                ],
                [run(0), ["platformio", "run", "-s", "-d", tmpdir]],
                [after(tmpdir), None]
            ]
        )

    for runner, cmd in commands:
        if not runner(cmd):
            return False

    return True


if __name__ == "__main__":
    root = os.environ.get("CI_PROJECT_DIR")
    if not root:
        root = os.getcwd()

    _, rel_path = sys.argv

    base = os.path.join(root, rel_path)
    libs = get_pio_libraries(cwd=base)

    print("preparing dependencies ...")
    if not pio_prepare(
        cwd=base,
        libraries=libs,
        platforms=("espressif8266@1.5.0", "espressif8266@1.7.3"),
    ):
        sys.exit(1)

    print("prepared dependencies")
