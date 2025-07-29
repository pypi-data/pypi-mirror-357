import os
import platform
import ctypes


class MMKV:
    def __init__(self, root_dir):
        system = platform.system()
        arch = platform.machine().lower()

        if system == "Windows":
            lib_name = "mmkv.cp39-win_amd64.pyd"
            subdir = "win_amd64"
        elif system == "Linux":
            lib_name = "mmkv.cpython-312-x86_64-linux-gnu.so"
            subdir = "linux_x86_64"
        elif system == "Darwin":
            lib_name = "mmkv.cpython-313-darwin.so"
            subdir = "darwin_x86_64"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        base_path = os.path.dirname(__file__)
        lib_path = os.path.join(base_path, "libs", subdir, lib_name)

        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"MMKV library not found: {lib_path}")

        self.lib = ctypes.CDLL(lib_path)
        self.lib.initializeMMKV.argtypes = [ctypes.c_char_p]
        self.lib.initializeMMKV.restype = None
        self.lib.initializeMMKV(root_dir.encode())

    def set(self, key: str, val: str):
        self.lib.setString.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.setString.restype = None
        self.lib.setString(key.encode(), val.encode())

    def get(self, key: str) -> str:
        self.lib.getString.argtypes = [ctypes.c_char_p]
        self.lib.getString.restype = ctypes.c_char_p