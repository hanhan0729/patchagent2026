CXX=$CXX
CXXFLAGS=$CXXFLAGS
LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
./autogen.sh --without-cython --enable-debug --without-tests
make -j$(nproc) clean
make -j$(nproc) all

for fuzzer in bplist_fuzzer xplist_fuzzer jplist_fuzzer oplist_fuzzer; do
  $CXX $CXXFLAGS -std=c++11 -Iinclude/ \
      fuzz/$fuzzer.cc -o ./$fuzzer \
      $LIB_FUZZING_ENGINE src/.libs/libplist-2.0.a
done

zip -j ./bplist_fuzzer_seed_corpus.zip test/data/*.bplist
zip -j ./xplist_fuzzer_seed_corpus.zip test/data/*.plist
zip -j ./jplist_fuzzer_seed_corpus.zip test/data/*.json
zip -j ./oplist_fuzzer_seed_corpus.zip test/data/*.ostep

cp fuzz/*.dict fuzz/*.options ./
