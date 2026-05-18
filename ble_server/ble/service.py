"""BLE service orchestration for RFID requests and JSON responses."""

from typing import Callable

from .characteristics import (
    BLECharacteristic,
    OBJECT_RESPONSE_DESCRIPTION,
    RFID_QUERY_DESCRIPTION,
)
from .uuids import (
    OBJECT_RESPONSE_CHARACTERISTIC_UUID,
    RFID_QUERY_CHARACTERISTIC_UUID,
    SERVICE_UUID,
)
from ..utils.json_utils import to_json_string


class WarehouseBLEService:
    """Coordinates BLE characteristic updates for warehouse lookups."""

    def __init__(self) -> None:
        self.service_uuid = SERVICE_UUID
        self.rfid_query_characteristic = BLECharacteristic(
            uuid=RFID_QUERY_CHARACTERISTIC_UUID,
            description=RFID_QUERY_DESCRIPTION,
        )
        self.object_response_characteristic = BLECharacteristic(
            uuid=OBJECT_RESPONSE_CHARACTERISTIC_UUID,
            description=OBJECT_RESPONSE_DESCRIPTION,
        )

    def handle_rfid_query(self, rfid_id: str, lookup_callback: Callable[[str], dict]) -> dict:
        self.rfid_query_characteristic.write(rfid_id.encode("utf-8"))
        response_payload = lookup_callback(rfid_id)
        response_json = to_json_string(response_payload)
        self.object_response_characteristic.write(response_json.encode("utf-8"))
        return response_payload
