
cmake . -DCMAKE_C_FLAGS="$CFLAGS" -DCMAKE_CXX_FLAGS="$CXXFLAGS"     \
        -DBUILD_FUZZERS=ON -DBUILD_TESTS=OFF -DBUILD_BENCHMARKS=OFF \
        -DBUILD_STATIC=ON -DBUILD_SHARED=OFF
make clean
make -j$(nproc)

zip -j ./decompress_fuzzer_seed_corpus.zip compat/*.cdata

find . -name '*_fuzzer' -exec cp -v '{}' . ';'
find . -name '*_fuzzer.dict' -exec cp -v '{}' . ';'
find . -name '*_fuzzer_seed_corpus.zip' -exec cp -v '{}' . ';'
