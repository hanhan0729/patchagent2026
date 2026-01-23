export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"

OUT=$PWD
BUILD=Build
fuzz_targets=(
    src/fe-fuzz/irssi-fuzz
    src/fe-fuzz/server-fuzz
    src/fe-fuzz/irc/core/event-get-params-fuzz
    src/fe-fuzz/fe-common/core/theme-load-fuzz
)

rm -rf "$BUILD"
mkdir -p "$BUILD"

meson "$BUILD" -Dstatic-dependency=yes -Dinstall-glib=force \
      -Dwith-fuzzer=yes -Dwith-fuzzer-lib=$LIB_FUZZING_ENGINE \
      -Dfuzzer-link-language=cpp \
    || ( cat "$BUILD"/meson-logs/meson-log.txt && false )

ninja -C "$BUILD" -v "${fuzz_targets[@]}"
( cd "$BUILD" && mv "${fuzz_targets[@]}" "$OUT" )
