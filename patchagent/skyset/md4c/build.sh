
mv ./{*.zip,*.dict} .

mkdir build && cd build
cmake ../ -DBUILD_SHARED_LIBS=OFF
make
$CC $CFLAGS -c ../test/fuzzers/fuzz-mdhtml.c -I../src
$CXX $CXXFLAGS -fsanitize=fuzzer fuzz-mdhtml.o -o ./fuzz-mdhtml \
    ./src/libmd4c-html.a ./src/libmd4c.a
cp ./fuzz-mdhtml ../