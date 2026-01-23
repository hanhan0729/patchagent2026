#!/bin/bash

./autogen.sh
./configure --disable-shared
make -j$(nproc)
