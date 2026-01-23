./autogen.sh \
    --disable-shared \
    --without-debug \
    --without-http \
    --without-python
make -j$(nproc)
make runtest
./runtest || exit 1
