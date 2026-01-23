
export OUT=$PWD
export SRC=$PWD
export WORK=$PWD
export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
./oss-fuzz-build.sh
