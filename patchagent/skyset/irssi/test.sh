meson Build
ninja -C Build
ninja -C Build test || exit -1
# libbrotli-dev libinih-dev xmlto