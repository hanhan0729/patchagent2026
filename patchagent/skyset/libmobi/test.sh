./autogen.sh
./configure --disable-shared
make -j$(nproc)
make test