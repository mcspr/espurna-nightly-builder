import os


def version_sub(filename, mask, template, **template_kv):
    """Parse known pattern '<mask>-<env>.bin' as:
    '<mask>': 'espurna-<version>-<build>'
    '<version>': '<major>.<minor>.<patch>[a-z]-<build>'
    '<build>': '-...' or nothing
    Then, substitute '<version>' with given template.

    Original is passed to the .format by using 'orig_version' keyword argument."""
    if mask not in filename:
        return filename

    app, delim, orig_version = mask.partition("-")
    if not delim:
        return filename

    template_kv["orig_version"] = orig_version
    new_version = template.format(**template_kv)

    return filename.replace(orig_version, new_version)


def rename_releases(releases_dir, version_template, **template_kv):
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
                new_filename = version_sub(
                    filename, mask, version_template, **template_kv
                )
                if new_filename == filename:
                    continue

                old_path = os.path.join(releases_dir, mask, filename)
                new_path = os.path.join(releases_dir, mask, new_filename)
                os.rename(old_path, new_path)
