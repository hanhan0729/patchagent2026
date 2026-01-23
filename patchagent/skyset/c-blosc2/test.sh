cmake -S '.' -B '.' -D DEACTIVATE_AVX2=ON -D CMAKE_BUILD_TYPE='Release' -D BUILD_SHARED_LIBS=OFF
cmake --build '.' --config 'Release'
ctest -C Release --output-on-failure --max-width 120 || exit 1
