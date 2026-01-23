ABSPATH=$(dirname $(readlink -f $0))
./autogen.sh \
    --without-debug \
    --without-http \
    --without-python
make -j

$CC -Iinclude -lxml2 -Wl,-rpath=$PWD/.libs -g $ABSPATH/poc-8f30bdf.c -o poc