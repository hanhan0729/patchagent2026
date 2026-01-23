export CFLAGS="-DNDEBUG"
export CXXFLAGS="-DNDEBUG"

cd tests/fuzz

make -j seedcorpora
./fuzz.py build all

for target in $(./fuzz.py list); do
    cp "$target" "../.."

    if [ -f "$target.dict" ]; then
        cp "$target.dict" "../.."
    fi

    cp "corpora/${target}_seed_corpus.zip" "../.."
done
