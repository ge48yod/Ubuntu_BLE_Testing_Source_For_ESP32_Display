"""Mock JSON-backed object storage and lookup helpers."""

import json
from pathlib import Path
from typing import Optional

from ..models.storage_info import StorageInfo


class ObjectStore:
    def __init__(self, json_path: Path) -> None:
        self.json_path = json_path
        self._objects = self._load()

    def _load(self) -> dict:
        with self.json_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def lookup(self, rfid_id: str) -> Optional[StorageInfo]:
        record = self._objects.get(rfid_id)
        if not record:
            return None
        return StorageInfo(**record)


def default_store() -> ObjectStore:
    base_path = Path(__file__).resolve().parent
    return ObjectStore(base_path / "objects.json")
