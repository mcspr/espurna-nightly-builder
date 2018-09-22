import os

from espurna_nightly_builder.util import git_head, nightly_tag

VERSION_FMT = "{version}.nightly{tag}.git{sha}"

# known pattern: '<mask>-<env>.bin'
# '<mask>': 'espurna-<version>'
# '<version>': '<major>.<minor>.<patch>[a-z]'
def rename_file(filename, tag, sha):
    _before, version, _after = filename.split("-", 2)
    version = VERSION_FMT.format(version=version, tag=tag, sha=sha)
    return "-".join([_before, version, _after])


def rename_releases(releases_dir, fmt=VERSION_FMT):
    """Search given directory for files and replace '<version>' in the name with given '<fmt>'"""
    sha = git_head(short=True, cwd=releases_dir)
    tag = nightly_tag()
    masks = []

    for dirpath, dirnames, filenames in os.walk(releases_dir):
        if dirpath == releases_dir:
            masks = dirnames
            continue

        # avoid recursive renaming by checking if filename already has ref
        for filename in filenames:
            for mask in masks:
                if filename.startswith(mask) and not sha in filename:
                    new_filename = rename_file(filename, tag, sha)
                    old_path = os.path.join(releases_dir, mask, filename)
                    new_path = os.path.join(releases_dir, mask, new_filename)
                    os.rename(old_path, new_path)
