#!/usr/bin/env python3

import os
import sys
import json
import tempfile
import subprocess


def build(llvmcc):
    argv = sys.argv[1:]
    file = tempfile.NamedTemporaryFile(delete=False)
    
    argv.append('-ldl')
    argv.append('-Wno-everything')

    subprocess.check_call(['bear', '--output', file.name, '--', llvmcc] + argv)
    
    log_path = os.getenv("BEAR_LOG_PATH")
    assert log_path is not None, "BEAR_LOG_PATH is not set"
    with open(file.name, 'r') as f:
        with open(log_path, 'a') as log:
            for item in json.load(f):
                log.write(json.dumps(item) + '\n')