mkdir _install
mkdir _build

pushd _build

cmake .. -DCMAKE_INSTALL_PREFIX=../_install \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_CXX_STANDARD=17 \
-DCMAKE_VERBOSE_MAKEFILE:BOOL='OFF' \
-DBUILD_SHARED_LIBS='ON' \
-DOPENEXR_INSTALL_TOOLS='ON' \
-DOPENEXR_INSTALL_DOCS='OFF' \
-DOPENEXR_RUN_FUZZ_TESTS='OFF'

cmake --build . \
--target install \
--config Release

ctest -T Test -C Release --timeout 7200 --output-on-failure -VV || exit 1

popd