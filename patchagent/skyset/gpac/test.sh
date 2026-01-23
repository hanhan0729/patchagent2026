#!/bin/bash
./configure
make -j
git submodule update --init
export PATH="$(realpath ./bin/gcc):$PATH"
cd testsuite
./make_tests.sh -sync-media -clean
./make_tests.sh -quick 2>/dev/null | grep "Tests passed"
# bsdmainutils