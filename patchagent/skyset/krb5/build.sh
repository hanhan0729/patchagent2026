export CC=$CC
export CXX=$CXX
export CFLAGS=$CFLAGS
export CXXFLAGS=$CXXFLAGS
pushd src/
autoreconf -f
./configure --enable-static --disable-shared CC=$CC CXX=$CXX CFLAGS="-fcommon $CFLAGS" CXXFLAGS="-fcommon $CXXFLAGS" LDFLAGS="-fcommon $CFLAGS"
make -j`nproc`
popd

cp -r ../fuzzing .
pushd fuzzing/
make -j`nproc` CFLAGS="-fsanitize=fuzzer" CXXFLAGS="-fsanitize=fuzzer"

cp Fuzz_chpw ../Fuzz_chpw
popd