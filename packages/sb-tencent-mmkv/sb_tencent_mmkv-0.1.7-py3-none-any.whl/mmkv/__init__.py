import ctypes
import os
import platform
import sys

def load_native_mmkv():
    base_dir = os.path.dirname(__file__)
    system = platform.system()

    if system == "Windows":
        lib_path = os.path.join(base_dir, "libs", "win_amd64", "mmkv.cp313-win_amd64.pyd")
    elif system == "Linux":
        lib_path = os.path.join(base_dir, "libs", "linux_x86_64", "mmkv.cpython-313-x86_64-linux-gnu.so")
    elif system == "Darwin":
        lib_path = os.path.join(base_dir, "libs", "darwin_x86_64", "mmkv.cpython-313-darwin.so")
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    return ctypes.CDLL(lib_path)

native_lib = load_native_mmkv()