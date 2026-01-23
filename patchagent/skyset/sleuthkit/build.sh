
export LIB_FUZZING_ENGINE="-fsanitize=fuzzer"
export CFLAGS="$CFLAGS -Wno-error=non-c-typedef-for-linkage"
export CXXFLAGS="$CXXFLAGS -Wno-error=non-c-typedef-for-linkage"

ABS_PATH=$(cd $(dirname $0) && pwd)
sed -i 's/-Werror//g' ./tsk/util/Makefile.am
sed -i 's/-Werror//g' ./tsk/pool/Makefile.am

${ABS_PATH}/buildcorpus.sh || true

./bootstrap
./configure --enable-static --disable-shared --disable-java --without-afflib --without-libewf --without-libvhdi --without-libvmdk
make -j$(nproc)

declare -A TSK_FS_TYPES=(
  ["ext"]="TSK_FS_TYPE_EXT_DETECT"
  ["fat"]="TSK_FS_TYPE_FAT_DETECT"
  ["hfs"]="TSK_FS_TYPE_HFS"
  ["ntfs"]="TSK_FS_TYPE_NTFS"
  ["iso9660"]="TSK_FS_TYPE_ISO9660"
)

declare -A TSK_VS_TYPES=(
  ["dos"]="TSK_VS_TYPE_DOS"
  ["gpt"]="TSK_VS_TYPE_GPT"
  ["mac"]="TSK_VS_TYPE_MAC"
  ["sun"]="TSK_VS_TYPE_SUN"
)

$CXX $CXXFLAGS -std=c++14 -I.. -I. -Itsk \
    ${ABS_PATH}/sleuthkit_fls_apfs_fuzzer.cc -o ./sleuthkit_fls_apfs_fuzzer \
    $LIB_FUZZING_ENGINE ./tsk/.libs/libtsk.a -lz

for type in ${!TSK_FS_TYPES[@]}; do
  $CXX $CXXFLAGS -std=c++14 -I.. -I. -Itsk -DFSTYPE=${TSK_FS_TYPES[$type]} \
      ${ABS_PATH}/sleuthkit_fls_fuzzer.cc -o ./sleuthkit_fls_${type}_fuzzer \
      $LIB_FUZZING_ENGINE ./tsk/.libs/libtsk.a -lz
done

for type in ${!TSK_VS_TYPES[@]}; do
  $CXX $CXXFLAGS -std=c++14 -I.. -I. -Itsk -DVSTYPE=${TSK_VS_TYPES[$type]} \
      ${ABS_PATH}/sleuthkit_mmls_fuzzer.cc -o ./sleuthkit_mmls_${type}_fuzzer \
      $LIB_FUZZING_ENGINE ./tsk/.libs/libtsk.a -lz
done
