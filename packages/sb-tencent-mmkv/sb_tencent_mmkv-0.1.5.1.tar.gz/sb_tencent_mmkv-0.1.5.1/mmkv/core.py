import os
import platform
import ctypes

class MMKVMode:
    SingleProcess = 1
    MultiProcess = 2

class MMKV:
    def __init__(self, mmap_id: str, mode=MMKVMode.SingleProcess):
        self.mmap_id = mmap_id.encode()
        self.mode = mode
        self.lib = load_native_lib()
        self.ptr = self.lib.getMMKVWithID(self.mmap_id, self.mode)
        if not self.ptr:
            raise RuntimeError("Failed to get MMKV instance")

    def set(self, key: str, val: str):
        self.lib.encodeString(self.ptr, key.encode(), val.encode())

    def getString(self, key: str):
        self.lib.getString.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.getString.restype = ctypes.c_char_p
        res = self.lib.getString(self.ptr, key.encode())
        return res.decode() if res else ""

    def setBool(self, key: str, val: bool):
        self.lib.encodeBool(self.ptr, key.encode(), ctypes.c_bool(val))

    def getBool(self, key: str):
        self.lib.getBool.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.getBool.restype = ctypes.c_bool
        return bool(self.lib.getBool(self.ptr, key.encode()))

    def setInt(self, key: str, val: int):
        self.lib.encodeInt(self.ptr, key.encode(), ctypes.c_int(val))

    def getInt(self, key: str):
        self.lib.getInt.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.getInt.restype = ctypes.c_int
        return int(self.lib.getInt(self.ptr, key.encode()))

    def setBytes(self, key: str, val: bytes):
        self.lib.encodeBytes(self.ptr, key.encode(), ctypes.c_char_p(val))

    def getBytes(self, key: str):
        self.lib.getBytes.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.getBytes.restype = ctypes.c_char_p
        return self.lib.getBytes(self.ptr, key.encode())

    def contains(self, key: str):
        self.lib.contains.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.contains.restype = ctypes.c_bool
        return bool(self.lib.contains(self.ptr, key.encode()))

    def remove_value(self, key: str):
        self.lib.removeValue.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.removeValue.restype = None
        self.lib.removeValue(self.ptr, key.encode())

    def clear_all(self):
        self.lib.clearAll.argtypes = [ctypes.c_void_p]
        self.lib.clearAll.restype = None
        self.lib.clearAll(self.ptr)

    def all_keys(self):
        self.lib.getAllKeys.restype = ctypes.POINTER(ctypes.c_char_p)
        keys_ptr = self.lib.getAllKeys(self.ptr)
        keys = []
        idx = 0
        while keys_ptr[idx]:
            keys.append(keys_ptr[idx].decode())
            idx += 1
        return keys

    @staticmethod
    def initializeMMKV(root_dir: str):
        lib = load_native_lib()
        lib.initializeMMKV(root_dir.encode())

    @staticmethod
    def backupOneToDirectory(mmap_id: str, path: str) -> bool:
        lib = load_native_lib()
        return lib.backupOneToDirectory(mmap_id.encode(), path.encode())

    @staticmethod
    def restoreOneFromDirectory(mmap_id: str, path: str) -> bool:
        lib = load_native_lib()
        return lib.restoreOneFromDirectory(mmap_id.encode(), path.encode())


def load_native_lib():
    system = platform.system()
    base_path = os.path.dirname(__file__)

    if system == "Windows":
        lib_path = os.path.join(base_path, "libs", "win_amd64", "mmkv.cp39-win_amd64.pyd")
    elif system == "Linux":
        lib_path = os.path.join(base_path, "libs", "linux_x86_64", "mmkv.cpython-312-x86_64-linux-gnu.so")
    elif system == "Darwin":
        lib_path = os.path.join(base_path, "libs", "darwin_x86_64", "mmkv.cpython-313-darwin.so")
    else:
        raise RuntimeError(f"Unsupported system: {system}")

    print(f"Loading native MMKV library from: {lib_path}")  # Debugging line

    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Native MMKV lib not found: {lib_path}")

    return ctypes.CDLL(lib_path)
