export CC=clang 
export CXX=clang++ 
export CFLAGS="-Wno-everything" 
export CXXFLAGS="-Wno-everything"
./autogen.sh
./configure
make -j
make check -j