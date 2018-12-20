import os

from espurna_nightly_builder.util import git_head, nightly_tag

VERSION_FMT = "{version}.nightly{tag}+git{sha:.8}"

# known pattern: '<mask>-<env>.bin'
# '<mask>': 'espurna-<version>-<build>'
# '<version>': '<major>.<minor>.<patch>[a-z]-<build>'
# '<build>': '-...' or nothing
def format_filename(filename, mask, template, **template_kv):
    _before, _, version = mask.partition("-")
    version = template.format(version=version, **template_kv)
    return filename.replace(mask, version)


def rename_releases(releases_dir, version_template=VERSION_FMT, **template_kv):
    """Search given directory for files and replace '<version>' in the name with given '<version_template>'"""
    masks = []

    # avoid renaming multiple times by checking if filename already has template values
    def _was_renamed(filename):
        for v in template_kv.values():
            if v in filename:
                return True

        return False

    for dirpath, dirnames, filenames in os.walk(releases_dir):
        if dirpath == releases_dir:
            masks = dirnames
            continue

        for filename in filenames:
            if _was_renamed(filename):
                continue
            for mask in masks:
                if not filename.startswith(mask):
                    continue
                new_filename = format_filename(
                    filename, mask, version_template, **template_kv
                )
                if new_filename == filename:
                    continue

                old_path = os.path.join(releases_dir, mask, filename)
                new_path = os.path.join(releases_dir, mask, new_filename)
                os.rename(old_path, new_path)
