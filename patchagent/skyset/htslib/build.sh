
autoconf
autoheader
./configure
make -j$(nproc) libhts.a test/fuzz/hts_open_fuzzer.o

$CXX $CXXFLAGS -o "./hts_open_fuzzer" test/fuzz/hts_open_fuzzer.o -fsanitize=fuzzer libhts.a -lz -lbz2 -llzma -lcurl -lcrypto -lpthread
