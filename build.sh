#!/bin/bash
set -e
pushd espurna/code

echo "!!! :_: !!!"

ENVIRONMENT=${1}
APP_REVISION=$(git rev-parse --short HEAD)
APP_VERSION=$(grep APP_VERSION espurna/config/version.h | awk '{print $3}' | sed 's/"//g')
OUTPUT_DIR="../firmware/espurna-${APP_VERSION}"

cp espurna/config/version.h espurna/config/version.h.original
sed -i -e "s/APP_REVISION            \".*\"/APP_REVISION            \"$APP_REVISION\"/g" espurna/config/version.h

time node node_modules/gulp/bin/gulp.js
time platformio run -s -e ${ENVIRONMENT}

mkdir -p ${OUTPUT_DIR}
cp .pioenvs/${1}/firmware.bin ${OUTPUT_DIR}/espurna-${APP_VERSION}.git${APP_REVISION}-${ENVIRONMENT}.bin

popd

