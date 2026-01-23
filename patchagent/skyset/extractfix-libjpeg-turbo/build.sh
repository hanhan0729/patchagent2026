cmake -G "Unix Makefiles" .
if [ $? -ne 0 ]; then
    autoreconf -fiv
    ./configure
fi
make -j$(nproc)