#!/bin/bash
set -e -o pipefail
pushd espurna/code

# Reuse parallel build implementation from https://github.com/xoseperez/espurna/pull/986 (kudos to @lobradov)
par_thread=${BUILDER_THREAD:-0}
par_total_threads=${BUILDER_TOTAL_THREADS:-4}
if [ ${par_thread} -ne ${par_thread} -o \
    ${par_total_threads} -ne ${par_total_threads} ]; then
    echo "Parallel threads should be a number."
    exit
fi
if [ ${par_thread} -ge ${par_total_threads} ]; then
    echo "Current thread is greater than total threads. Doesn't make sense"
    exit
fi

environments=$(grep env: platformio.ini | grep -v ota  | grep -v ssl  | grep -v travis | sed 's/\[env://' | sed 's/\]/ /' | sort)
environments=$(echo ${environments} | \
    awk -v par_thread=${par_thread} -v par_total_threads=${par_total_threads} \
    '{ for (i = 1; i <= NF; i++) if (++j % par_total_threads == par_thread ) print $i; }')

APP_REVISION=$(git rev-parse --short HEAD)
APP_VERSION=$(grep APP_VERSION espurna/config/version.h | awk '{print $3}' | sed 's/"//g')
OUTPUT_DIR="../firmware/espurna-${APP_VERSION}"

[[ $TRAVIS = "true" ]] && time node node_modules/gulp/bin/gulp.js

mkdir -p ${OUTPUT_DIR}
for environment in $environments ; do
    echo "> $environment"
    time platformio run -s -e $environment
    cp .pioenvs/$environment/firmware.bin ${OUTPUT_DIR}/espurna-${APP_VERSION}.git${APP_REVISION}-${environment}.bin
    break
done

popd

