mkdir -p build
pushd build
cmake -DBUILD_WASI=none ..
make -j$(nproc)
popd

$CC $CFLAGS -c platforms/app_fuzz/fuzzer.c -o fuzzer.o -Isource
$CXX $CXXFLAGS -fsanitize=fuzzer -o fuzzer fuzzer.o build/source/libm3.a
