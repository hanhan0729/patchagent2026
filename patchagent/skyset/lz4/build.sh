export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
export CFLAGS=$CFLAGS
export CXXFLAGS=$CXXFLAGS
export LDFLAGS=$LDFLAGS
export CC=$CC
export CXX=$CXX
export LD=$LD
export OUT=.
./ossfuzz/ossfuzz.sh
