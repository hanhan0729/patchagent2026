pushd src/
autoreconf -f
./configure 
make -j`nproc`
make check || exit -1
popd