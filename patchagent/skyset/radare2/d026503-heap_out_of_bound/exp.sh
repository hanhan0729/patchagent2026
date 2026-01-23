LD_LIBRARY_PATH=./libr/:./lib/:$LD_LIBRARY_PATH ASAN_OPTIONS=$ASAN_OPTIONS:detect_leaks=0:abort_on_error=1:symbolize=1:allocator_may_return_null=1:detect_odr_violation=0 ./bin/r2 -A -q @POC@


