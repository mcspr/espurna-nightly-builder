# ESPurna Nightly Builder
[![latest release tag](https://img.shields.io/github/release/mcspr/espurna-nightly-builder/all.svg?label=Latest%20release)](https://github.com/mcspr/espurna-nightly-builder/releases)
[travis-ci.org build logs](https://travis-ci.org/mcspr/espurna-nightly-builder/builds)

# Nightly build?

This repo is used to build binary release of [ESPurna](https://github.com/xoseperez/espurna), every night at **04:10 UTC**  
Unlike official releases, binaries are created from latest commit to the [`dev`](https://github.com/xoseperez/espurna/tree/dev) branch.

# Technical info
[Travis CI Cron](https://docs.travis-ci.com/user/cron-jobs/) is used to trigger the build. See [.travis.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.travis.yml) and [espurna_nightly_builder](https://github.com/mcspr/espurna-nightly-builder/tree/builder/espurna_nightly_builder) scripts.

Build process is split into 2 stages - Test and Release.

## Test

This stage performs multiple tests and stops the build when they fail.
- Build can be triggered either from Cron or through Travis CI API. Following tests will run only when triggered from Cron. API will start building immediately.
- CI test status of the latest 'dev' commit. If testing fails, full release is likely to fail too.
- If 'master' branch has the same commit as 'dev'. This will happen when official release has been made. If yes - there is no need to repeat build here.
- Compare contents of 'commit.txt' file on the 'nightly' branch and SHA hash value of the latest 'dev' branch commit. To avoid repeated builds it will stop build process when they are the same. 

Finally, SHA value of the latest 'dev' branch commit is added to the 'nightly' branch via plain text file 'commit.txt'. Then, new release is created for that commit. This automatically tags the commit and creates release in the 'Releases' section.

## Release

This stage runs the same build.sh script that is used to build official releases. Only difference is — after it is done, files are renamed to include current date (tag of the release) and git SHA hash value ('commit.txt' contents from the previous stage).

# GitLab

> Incomplete and not working right now

[.gitlab-ci.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.gitlab-ci.yml) uses the same process as Travis build script, but with notable differences:
- Custom container image (see [Dockerfile](https://github.com/mcspr/espurna-nightly-builder/blob/builder/Dockerfile)) is used
- It is pretending to be Travis for [build.sh](https://github.com/mcspr/espurna-nightly-builder/blob/f702837ed95bf1174584269e7fd6f75fe4acf85c/.gitlab-ci.yml#L65)
- [Build takes more time than travis](https://gitlab.com/mcspr/espurna-travis-test/pipelines/25418527)

# TODO

- [ ] GitHub commit status / GitHub Checks for 'nightly' branch
- [ ] Hide commit status for 'builder' branch
- [ ] Hide releases until build is complete
- [ ] Redo build completely when triggered by API (remove tag, release and it's assets)
- [ ] GitLab integration
