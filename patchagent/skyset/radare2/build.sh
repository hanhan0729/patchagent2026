#!/bin/bash
./configure --prefix=$(pwd) CC=$CC CXX=$CXX --with-capstone4 && make -j && make install