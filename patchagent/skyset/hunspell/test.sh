autoreconf -vfi
./configure
make -j`nproc`
make check