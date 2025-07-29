import json
from .core import MMKV

class MMKVHelper:
    def __init__(self, storage_path: str, mmap_id: str):
        self.storage_path = storage_path
        self.mmap_id = mmap_id
        self.kv = MMKV(storage_path)

    def encode(self, data: dict):
        for k, v in data.items():
            self.kv.set(k, json.dumps(v))

    def decode(self, keys: list[str]) -> dict:
        return {k: json.loads(self.kv.get(k)) for k in keys if self.kv.get(k)}