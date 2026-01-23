mkdir build
cd build
cmake .. -G 'Unix Makefiles' -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-Wall -Wextra" -DCMAKE_VERBOSE_MAKEFILE=ON
cmake --build . --config Release
ctest || exit 1
