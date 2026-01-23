ABSPATH=$(dirname $(readlink -f $0))
./autogen.sh \
    --disable-shared \
    --without-debug \
    --without-http \
    --without-python
make -j
