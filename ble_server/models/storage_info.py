"""Storage object model returned to BLE clients."""

from dataclasses import asdict, dataclass


@dataclass
class StorageInfo:
    objectName: str
    location: str

    def to_dict(self) -> dict:
        return asdict(self)
