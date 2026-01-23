cd src
make -j
cd ..
cd tests
make -j
./test-aes || exit 1
./test-list || exit 1 
./test-md4 || exit 1 
./test-milenage || exit 1