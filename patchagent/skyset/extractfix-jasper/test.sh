sed -i 's/inline bool jas_safe_size_mul/bool jas_safe_size_mul/g' src/libjasper/base/jas_malloc.c
autoreconf -i
./configure --disable-libjpeg --disable-opengl
make -j
make check || exit 1