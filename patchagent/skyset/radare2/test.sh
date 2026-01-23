CC=clang
CXX=clang++
./configure --prefix=$(pwd) CC=$CC CXX=$CXX --with-capstone4 && make -j && make install
export PATH="$(realpath ./bin):$PATH"
export LD_LIBRARY_PATH=$(realpath ./libr/):$(realpath ./lib/):$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$(realpath ./lib/pkgconfig):$PKG_CONFIG_PATH
subdirs=$(find ./libr -type d)
for subdir in $subdirs; do
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(realpath $subdir)
done
pushd test
make unit -j || exit 1
./run_unit.sh || exit 1
popd
