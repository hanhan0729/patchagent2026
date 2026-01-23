
cd 'tests'

export LDO=$CXX
export LDFLAGS="$CXXFLAGS -fsanitize=fuzzer"
export CFLAGS="$CFLAGS -MMD"

export FUZZ_FLAGS=

for target in fuzzing/*; do
  [[ -d "$target" ]] || continue

  (
    cd "$target"
    make clean

    if [[ "$target" == "fuzzing/tls-server" ]]; then
      export CFLAGS="$CFLAGS -DCERTDIR='\"hwsim/auth_serv/\"'"
    fi

    make -j$(nproc) V=1 LIBFUZZER=y
  )
done
