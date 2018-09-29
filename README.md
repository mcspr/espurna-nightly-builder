[![latest release tag](https://img.shields.io/github/release/mcspr/espurna-nightly-builder/all.svg?label=Latest%20release)](https://github.com/mcspr/espurna-nightly-builder/releases/latest)
[![latest release date](https://img.shields.io/github/release-date-pre/mcspr/espurna-nightly-builder.svg)](https://github.com/mcspr/espurna-nightly-builder/releases/latest)  
[travis-ci.org build logs](https://travis-ci.org/mcspr/espurna-nightly-builder/builds)

# Nightly build?

This repo is used to build binary release of the latest [ESPurna](https://github.com/xoseperez/espurna)'s [`dev`](https://github.com/xoseperez/espurna/tree/dev) branch commit on a daily basis. Build starts every day at **04:10 UTC** using the [Travis CI Cron](https://docs.travis-ci.com/user/cron-jobs/). If there were no new commits since the latest release, build process will not create a new one.

# Technical info

> Note: See [espurna_nightly_builder](https://github.com/mcspr/espurna-nightly-builder/tree/builder/espurna_nightly_builder) and [.travis.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.travis.yml) scripts.

Build process is split into 2 stages - Test and Release.

## Test

This stage performs multiple tests and stops the build when they fail.
- Build can be triggered either from Cron or through Travis CI API. Following tests will run only when triggered from Cron. API will start building immediately.
- CI test status of the latest 'dev' commit. If testing fails, full release is likely to fail too.
- If 'master' branch has the same commit as 'dev'. This will happen when official release has been made. If yes - there is no need to repeat build here.
- Compare contents of 'commit.txt' file on the 'nightly' branch and sha value of the latest 'dev' branch commit. To avoid repeated builds it will stop build process when they are the same. 

Finally, sha value of the latest 'dev' branch commit is added to the 'nightly' branch via plain text file 'commit.txt'. Then, new release is created for that commit. This automatically tags the commit and creates release in the 'Releases' section.

## Release

This stage runs the same build.sh script that is used to build official releases. Only difference is — after it is done, files are renamed to include current date (tag of the release) and git sha value ('commit.txt' contents from the previous stage).

# GitLab

> Incomplete and not working right now

[.gitlab-ci.yml](https://github.com/mcspr/espurna-nightly-builder/blob/builder/.gitlab-ci.yml) uses the same process as Travis build script, but with notable differences:
- Custom container image (see [Dockerfile](https://github.com/mcspr/espurna-nightly-builder/blob/builder/Dockerfile)) is used
- It is pretending to be Travis for [build.sh](https://github.com/mcspr/espurna-nightly-builder/blob/f702837ed95bf1174584269e7fd6f75fe4acf85c/.gitlab-ci.yml#L65)
- [Build takes more time than travis](https://gitlab.com/mcspr/espurna-travis-test/pipelines/25418527)

# TODO

- [ ] GitHub commit status / GitHub Checks
- [ ] Hide releases until build is complete
- [ ] Redo build completely when triggered by API (remove tag, release and it's assets)
- [ ] GitLab integration
