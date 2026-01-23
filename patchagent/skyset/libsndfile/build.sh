

export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
export OUT=$PWD

export BUILD_ROOT=$PWD

echo "CC: ${CC:-}"
echo "CXX: ${CXX:-}"
echo "LIB_FUZZING_ENGINE: ${LIB_FUZZING_ENGINE:-}"
echo "CFLAGS: ${CFLAGS:-}"
echo "CXXFLAGS: ${CXXFLAGS:-}"
echo "OUT: ${OUT:-}"

export MAKEFLAGS+="-j$(nproc)"

./autogen.sh
./configure --disable-shared --enable-ossfuzzers
make V=1

cp -v ossfuzz/sndfile_fuzzer $OUT/

for fuzzer in sndfile_alt_fuzzer sndfile_fuzzer; do
  echo "[libfuzzer]" > ${OUT}/${fuzzer}.options
  echo "close_fd_mask = 3" >> ${OUT}/${fuzzer}.options
done
