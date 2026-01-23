CC=$CC
CXX=$CXX
CFLAGS=$CFLAGS
CXXFLAGS=$CXXFLAGS
LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
WORK=.
sed -i 's/^CFLAGS.*//g' Makefile
make -j$(nproc) libhoedown.a

$CC $CFLAGS -c -std=c99 -Isrc \
    "./test/hoedown_fuzzer.c" -o $WORK/hoedown_fuzzer.o
$CXX $CXXFLAGS -std=c++11 -Isrc \
    $WORK/hoedown_fuzzer.o -o ./hoedown_fuzzer \
    $LIB_FUZZING_ENGINE "./libhoedown.a"