CC=clang CXX=clang++ CFLAGS="-Wno-everything" ./configure --disable-shared --disable-gdb --disable-libdecnumber --disable-readline --disable-sim
make -j
make check || exit 1