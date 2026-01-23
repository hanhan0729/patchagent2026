LD_LIBRARY_PATH=./lib/:./libr/:$LD_LIBRARY_PATH ASAN_OPTIONS=$ASAN_OPTIONS:detect_odr_violation=0 ./bin/r2 -q -A  @POC@
