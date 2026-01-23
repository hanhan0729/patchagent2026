export V=1

./autogen.sh \
    --disable-shared \
    --without-debug \
    --without-http \
    --without-python
make -j$(nproc)

cd fuzz
make clean-corpus
make fuzz.o

for fuzzer in html regexp schema uri valid xinclude xml xpath; do
    make $fuzzer.o
    # Link with $CXX
    $CXX $CXXFLAGS \
        $fuzzer.o fuzz.o \
        -o ./$fuzzer \
        -fsanitize=fuzzer \
        ../.libs/libxml2.a -Wl,-Bstatic -lz -llzma -Wl,-Bdynamic

    cp ./$fuzzer ../
done

