export CC=clang
export CXX=clang++
export CFLAGS="-Wno-everything"
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
make -j
make check -j
if [ $? -eq 0 ]; then
    exit 0
fi

echo $commit
if [ $commit = "8d34b45" ]; then
    if grep "FAIL:  2" ./tests/test-suite.log; then
        echo "SUCCESS"
        exit 0
    fi
    if grep "FAIL:  1" ./tests/test-suite.log; then
        echo "SUCCESS"
        exit 0
    fi
fi
if [ $commit = "68c5eec" ]; then
    if grep "FAIL:  3" ./tests/test-suite.log; then
        echo "SUCCESS"
        exit 0
    fi
fi
if [ $commit = "ca99c52" ]; then
    if grep "FAIL:  3" ./tests/test-suite.log; then
        echo "SUCCESS"
        exit 0
    fi
fi
if [ $commit = "658529a" ]; then
    if grep "FAIL:  4" ./tests/test-suite.log; then
        echo "SUCCESS"
        exit 0
    fi
fi
exit 1