ABSPATH=$(cd "$(dirname "$0")"; pwd)

commit=$(git rev-parse HEAD)
commit=${commit:0:7}

./bootstrap
pushd gnulib
if [ -f $ABSPATH/$commit.patch ]; then
    if git apply --check $ABSPATH/$commit.patch; then
        git apply $ABSPATH/$commit.patch
    fi
fi
popd
cp gnulib/lib/fseeko.c lib/fseeko.c
FORCE_UNSAFE_CONFIGURE=1 ./configure 
if [ $commit = "658529a" ]; then ## HACK ASAN Error
    make -j || true
else
    make -j
fi