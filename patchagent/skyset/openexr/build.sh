CMAKE_SETTINGS=(
  "-D BUILD_SHARED_LIBS=OFF"         # Build static libraries only
  "-D BUILD_TESTING=OFF"             # Or tests
  "-D OPENEXR_INSTALL_EXAMPLES=OFF"  # Or examples
  "-D OPENEXR_LIB_SUFFIX="           # Don't append the version number to library files
)
cmake . ${CMAKE_SETTINGS[@]}
make -j$(nproc)

INCLUDES=(
  "-I ."
  "-I src/lib/OpenEXRCore"
  "-I src/lib/OpenEXR"
  "-I src/lib/OpenEXRUtil"
  "-I cmake"
)

LIBS=(
  "src/lib/OpenEXRUtil/libOpenEXRUtil.a"
  "src/lib/OpenEXR/libOpenEXR.a"
  "src/lib/OpenEXRCore/libOpenEXRCore.a"
  "src/lib/IlmThread/libIlmThread.a"
  "src/lib/Iex/libIex.a"
  "_deps/imath-build/src/Imath/libImath*.a"
)

for fuzzer in src/test/OpenEXRFuzzTest/oss-fuzz/*_fuzzer.cc; do
  fuzzer_basename=$(basename -s .cc $fuzzer)
  $CXX $CXXFLAGS -std=c++11 -pthread ${INCLUDES[@]} $fuzzer -fsanitize=fuzzer ${LIBS[@]} -lz \
    -o ./$fuzzer_basename
done
