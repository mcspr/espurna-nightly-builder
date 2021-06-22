import argparse
import logging
import os
import sys


from . import errors
from .api import Repo, Api, CommitRange
from .prepare import prepare
from .setup_repo import setup_repo
from .util import nightly_tag, last_month_prefix


logging.basicConfig(
    level=logging.INFO, format="%(relativeCreated)6d %(levelname)-8s %(message)s"
)
log = logging.getLogger("main")


def exc_handler(exc_type, exc_value, exc_trace):
    if issubclass(exc_type, errors.Error):
        log.error('Exiting: "{}"'.format(exc_value))
    else:
        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_trace))


sys.excepthook = exc_handler


def api_client(args):
    if not hasattr(api_client, "instance"):
        api_client.instance = Api(args.token)

    return api_client.instance


def f_prepare(args):
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


def f_setup_repo(args):
    setup_repo(branch=args.builder_branch, commit_filename=args.commit_filename)


def f_list_tags(args):
    builder_repo = Repo(args.builder_repo, api=api_client(args))

    tags = builder_repo.tags()
    log.info("tags:\n%s", "\n".join([tag["name"] for tag in tags]))


def f_delete_releases(args):
    builder_repo = Repo(args.builder_repo, api=api_client(args))

    prefix = args.prefix

    tags = builder_repo.tags()

    releases = builder_repo.releases(last=len(tags))
    releases = [
        release
        for release in releases
        if (release["tagName"] and release["tagName"].startswith(prefix))
        or "untagged" in release["url"]
    ]

    for release in releases:
        log.info("tagName:%(tagName)s number:%(number)d", release)
        if builder_repo.delete_release(release["number"]):
            log.info("deleted release")
        else:
            log.error("could not delete the release")
        if builder_repo.delete_tag(release["tagName"]):
            log.info("deleted tag")
        else:
            log.error("could not delete the tag")


def f_show_latest(args):
    builder_repo = Repo(args.builder_repo, api=api_client(args))

    head = builder_repo.branches(args.builder_branch)
    sha = head["commit"]["sha"]
    message = head["commit"]["commit"]["message"]
    log.info("builder head:%s message:%s", sha, message)

    target_commit = builder_repo.file(sha, args.commit_filename).content
    log.info("head target:%s", target_commit)


def f_testtagging(args):
    builder_repo = Repo(args.builder_repo, api=api_client(args))

    ref_string = "tags/{}".format(args.tag)

    print("creating tag", args.tag)
    print("for sha", args.sha)

    tag = builder_repo.add_tag(args.tag, "some tag message", args.sha)

    print("creating ref", ref_string)
    builder_repo.add_ref("refs/{}".format(ref_string), tag["sha"])

    print("tag sha is", tag["sha"])
    print("created tag for", tag["object"]["sha"])

    print("waiting...")
    input()

    print("deleting ref")
    builder_repo.delete_ref("refs/{}".format(ref_string))
    input()

    print("deleting tag")
    builder_repo.delete_tag(tag["sha"])
    input()


def f_mkoutputs(args):
    builder_repo = Repo(args.builder_repo, api=api_client(args))

    ref = builder_repo.ref_object("tags/{}".format(args.tag))
    tag = builder_repo.tag_object(ref["object"]["sha"])
    commit = builder_repo.commit_object(tag["object"]["sha"])

    print("tag is", args.tag)
    print("tag sha", tag["sha"])
    print("points to commit", commit["sha"])
    print("tag message is", tag["message"])
    print("commit message is", commit["message"])

    nightly_commit = builder_repo.file(commit["sha"], args.commit_filename)
    print("target commit is", nightly_commit.content)


def setup_argparse():
    parser = argparse.ArgumentParser()

    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--commit-filename", default="commit.txt")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--builder-branch", default="nightly")
    parser.set_defaults(func=lambda _: parser.print_help())

    subparser = parser.add_subparsers()

    cmd_setup_repo = subparser.add_parser("setup-repo", help=setup_repo.__doc__)
    cmd_setup_repo.set_defaults(func=f_setup_repo)

    cmd_prepare = subparser.add_parser("prepare", help=prepare.__doc__)
    cmd_prepare.add_argument("--source-directory", default="code/")
    cmd_prepare.add_argument("target_repo")
    cmd_prepare.add_argument("builder_repo")
    cmd_prepare.set_defaults(func=f_prepare)

    cmd_list_tags = subparser.add_parser("list-tags")
    cmd_list_tags.add_argument("builder_repo")
    cmd_list_tags.set_defaults(func=f_list_tags)

    cmd_delete = subparser.add_parser("delete-releases")
    cmd_delete.add_argument("--prefix", default=last_month_prefix())
    cmd_delete.add_argument("builder_repo")
    cmd_delete.set_defaults(func=f_delete_releases)

    cmd_mkoutputs = subparser.add_parser("mkoutputs")
    cmd_mkoutputs.add_argument("--tag", required=True)
    cmd_mkoutputs.add_argument("builder_repo")
    cmd_mkoutputs.set_defaults(func=f_mkoutputs)

    cmd_show_latest = subparser.add_parser("show-latest")
    cmd_show_latest.add_argument("builder_repo")
    cmd_show_latest.set_defaults(func=f_show_latest)

    cmd_test = subparser.add_parser("test-tagging")
    cmd_test.add_argument("--tag")
    cmd_test.add_argument("--sha")
    cmd_test.add_argument("builder_repo")
    cmd_test.set_defaults(func=f_testtagging)

    return parser


def main():
    parser = setup_argparse()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
