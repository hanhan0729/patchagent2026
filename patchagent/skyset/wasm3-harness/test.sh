mkdir build
pushd build
cmake ..
popd

cmake --build build

pushd test

python3 run-spec-test.py || exit 1
python3 run-spec-test.py --spec=v1.1 || exit 1
python3 run-wasi-test.py || exit 1

popd
