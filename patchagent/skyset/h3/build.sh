export CC=$CC
export CXX=$CXX
export CFLAGS=$CFLAGS
export CXXFLAGS=$CXXFLAGS
export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
export H3_BASE=.
mkdir build
cd build
cmake ..
make -j$(nproc) h3
cd ..

H3_BASE=`realpath .`

fuzzer_basename="fuzzerLocalIj"
fuzzer="$H3_BASE/src/apps/fuzzers/fuzzerLocalIj.c"
# H3_USE_LIBFUZZER is needed so that H3 does not try to build its own
# implementation of `main`
$CC $CFLAGS -DH3_PREFIX="" \
  -DH3_USE_LIBFUZZER=1 \
  -I$H3_BASE/src/apps/applib/include \
  -I$H3_BASE/src/h3lib/include \
  -I$H3_BASE/build/src/h3lib/include \
  -o $fuzzer_basename.o \
  -c $fuzzer

$CXX $CXXFLAGS $LIB_FUZZING_ENGINE -rdynamic \
  $fuzzer_basename.o \
  -o ./$fuzzer_basename \
  build/lib/libh3.a
