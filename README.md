# ESPurna Nightly Builder
[![latest nightly build](https://img.shields.io/github/release/mcspr/espurna-nightly-builder/all.svg?label=Latest%20nightly)](https://github.com/mcspr/espurna-nightly-builder/releases)
[![.github/workflows/lint.yml](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/lint.yml/badge.svg?branch=builder)](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/lint.yml)
[![.github/workflows/prepare.yml](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/prepare.yml/badge.svg?branch=builder)](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/prepare.yml)
[![.github/workflows/nightly.yml](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/nightly.yml/badge.svg?branch=builder)](https://github.com/mcspr/espurna-nightly-builder/actions/workflows/nightly.yml)

# Nightly build?

This repo is used to build binary release of [ESPurna](https://github.com/xoseperez/espurna).  
Unlike official releases, binaries are created from latest commit to the [`dev`](https://github.com/xoseperez/espurna/tree/dev) branch.

# Technical info
[Scheduled events](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#scheduled-events) are used to trigger the build. See [.github/workflows/prepare.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.github/workflows/prepare.yml), [.github/workflows/nightly.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.github/workflows/nightly.yml) and [espurna\_nightly\_builder helper scripts](https://github.com/mcspr/espurna-nightly-builder/tree/builder/espurna_nightly_builder).

Both workflows can be triggered with [a workflow\_dispatch event](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#manual-events).

## prepare.yml

See [.github/workflows/prepare.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.github/workflows/prepare.yml)  

This workflow is (supposed to be) triggered on a schedule. Unless the following tests pass, this stage will result in an error:
- The commit that 'dev' branch points at is different from the 'commit.txt' contents.
- All [Checks](https://docs.github.com/en/rest/reference/checks) of the target repository 'dev' branch are successful.
- 'master' branch does not point to the same commit as 'dev', as we don't want to re-do the official release.

Finally, the ['commit.txt'](https://github.com/mcspr/espurna-nightly-builder/blob/nightly/commit.txt) is updated with the latest SHA value of the 'dev' branch.

## nightly.yml

See [.github/workflows/nightly.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.github/workflows/nightly.yml)  

When 'prepare.yml' is successful or user triggers the workflow manually:
- 'nightly' branch is fetched with fetch depth 2, and HEAD and HEAD~1 'commit.txt' contents are saved.
- Target repository is fetched using the HEAD commit and the [generate\_release\_sh.py](https://github.com/xoseperez/espurna/blob/dev/code/scripts/generate_release_sh.py) script is called (which is also used to build the official releases)
- New pre-release is created with a tag YYYYMMDD, based on the latest modification date of the 'commit.txt'. Body should contain the HEAD~1...HEAD comparison URL.
- All of .bin files are uploaded as assets of the pre-release.

## Known issues

> Incomplete and not working right now

[.gitlab-ci.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.gitlab-ci.yml) uses the same process as original Travis build script, but with notable differences:
- Custom container image (see [Dockerfile](https://github.com/mcspr/espurna-nightly-builder/blob/builder/Dockerfile)) is used
- It is pretending to be Travis for [build.sh](https://github.com/mcspr/espurna-nightly-builder/blob/f702837ed95bf1174584269e7fd6f75fe4acf85c/.gitlab-ci.yml#L65)
- [Build takes more time than travis](https://gitlab.com/mcspr/espurna-travis-test/pipelines/25418527)

# TODO

- [x] GitHub commit status / GitHub Checks for 'nightly' branch
- [x] Hide commit status for 'builder' branch
- [x] Hide releases until build is complete
- [x] Redo build completely when triggered by API (remove tag, release and it's assets)
- [ ] GitLab integration
