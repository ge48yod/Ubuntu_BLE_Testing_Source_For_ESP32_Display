"""Simple BLE characteristic models used by the mock server."""

from dataclasses import dataclass

from .uuids import OBJECT_RESPONSE_CHARACTERISTIC_UUID, RFID_QUERY_CHARACTERISTIC_UUID


@dataclass
class BLECharacteristic:
    """Minimal characteristic container to keep the BLE flow beginner-readable."""

    uuid: str
    description: str
    value: bytes = b""

    def write(self, value: bytes) -> None:
        self.value = value

    def read(self) -> bytes:
        return self.value


RFID_QUERY_DESCRIPTION = "RFID query input"
OBJECT_RESPONSE_DESCRIPTION = "Object information JSON response"
