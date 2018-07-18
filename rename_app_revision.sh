#!/bin/bash
set -e -o pipefail

APP_REVISION=$(git -C espurna rev-parse --short HEAD)
APP_VERSION=$(grep APP_VERSION espurna/code/espurna/config/version.h | awk '{print $3}' | sed 's/"//g')

OLD_MASK=espurna-${APP_VERSION}
NEW_MASK=espurna-${APP_VERSION}-git${APP_REVISION}
BIN_DIR="espurna/firmware/espurna-${APP_VERSION}"

for fwbin in ${BIN_DIR}/* ; do
    new_fwbin=$(basename $fwbin)
    new_fwbin=${BIN_DIR}/${new_fwbin/${OLD_MASK}/${NEW_MASK}}
    mv -v $fwbin $new_fwbin
done

popd
