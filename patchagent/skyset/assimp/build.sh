cmake CMakeLists.txt -G "Ninja" -DBUILD_SHARED_LIBS=OFF -DASSIMP_BUILD_ZLIB=ON \
                                -DASSIMP_BUILD_TESTS=OFF -DASSIMP_BUILD_ASSIMP_TOOLS=OFF \
                                -DASSIMP_BUILD_SAMPLES=OFF
cmake --build .

# Build the fuzzer
$CXX $CXXFLAGS -fsanitize=fuzzer -std=c++11 -Iinclude \
		fuzz/assimp_fuzzer.cc -o assimp_fuzzer  \
		./lib/libassimp.a ./contrib/zlib/libzlibstatic.a
