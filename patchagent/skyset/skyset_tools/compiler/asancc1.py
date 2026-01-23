#!/usr/bin/env python3

import os
import subprocess
import sys

def check_and_append(argv, flag):
    # Append flag if not already in argv
    if flag not in argv:
        argv.append(flag)

def build(llvmcc):
    argv = sys.argv[1:]
    
    # If we do not remove all optimization flags, the sanitizer report may miss some inline functions and line numbers
    argv = list(filter(lambda x: not x.startswith('-O') and not x.startswith('-g'), argv))
    
    check_and_append(argv, '-g')
    check_and_append(argv, '-O0')
    check_and_append(argv, '-U_FORTIFY_SOURCE')
    check_and_append(argv, '-fno-omit-frame-pointer')
    
    # Configure AddressSanitizer (ASan) shared library
    asan_shared = 'libclang_rt.asan-x86_64.so'
    libclang_rt_asan_path = subprocess.getoutput(f"{llvmcc} -print-file-name={asan_shared}").strip(asan_shared)
    assert os.path.exists(libclang_rt_asan_path)
    
    check_and_append(argv, '-fsanitize=address')
    check_and_append(argv, '-Wl,--rpath=' + libclang_rt_asan_path)
    check_and_append(argv, '-shared-libasan')
    
    # Link with dynamic loader library and disable all warnings
    check_and_append(argv, '-ldl')
    check_and_append(argv, '-Wno-everything')

    # Execute the compilation command
    subprocess.check_call([llvmcc] + argv, env=os.environ)
