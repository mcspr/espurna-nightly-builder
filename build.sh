#!/bin/bash

pushd espurna/code
./build.sh ${1}
find ../firmware/
popd

