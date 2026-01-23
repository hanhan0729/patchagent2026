LD_LIBRARY_PATH=./libr/:./lib/:$LD_LIBRARY_PATH ASAN_OPTIONS=$ASAN_OPTIONS:detect_leaks=0:abort_on_error=1:symbolize=1:allocator_may_return_null=1:detect_odr_violation=0 ./bin/r2 -A -q @POC@

# radare2 5.8.9 31591 @ linux-arm-64
# birth: git.5.8.8-409-g95b648f090 2023-12-11__17:23:25
# commit: 95b648f0907e91e10d55fc48147a7dae99029c5b
