import os
import sys

from pathlib import Path

CONDA_PREFIX = os.environ['CONDA_PREFIX']
LLVMLITE_DIR = Path(__file__).parent
VER = sys.version_info
PYTHON_INCLUDE_NAME = f'python{VER.major}.{VER.minor}'

CONDA_INCLUDE_DIR = Path(CONDA_PREFIX, 'include')
PYTHON_INCLUDE_DIR = Path(CONDA_INCLUDE_DIR, PYTHON_INCLUDE_NAME)
FFI_DIR = Path(LLVMLITE_DIR, 'ffi')

flags = [
    f'-I{CONDA_INCLUDE_DIR}',
    f'-I{PYTHON_INCLUDE_DIR}',
    f'-I{FFI_DIR}',
    '-std=c++17',
    '-x', 'c++',
]


def Settings(**kwargs):
    return {'flags': flags}


if __name__ == '__main__':
    print(Settings())
