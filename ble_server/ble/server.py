"""BLE server facade for local mock backend behavior."""

import asyncio

from .service import WarehouseBLEService
from ..database.object_store import ObjectStore
from ..mock.mock_responses import object_found_response, object_not_found_response
from ..utils.json_utils import to_pretty_json
from ..utils.logger import get_logger


class BLEWarehouseServer:
    """Beginner-friendly BLE server flow with mock CLI support."""

    def __init__(self, store: ObjectStore) -> None:
        self.store = store
        self.logger = get_logger()
        self.service = WarehouseBLEService()

    async def start(self) -> None:
        self.logger.info("BLE service UUID: %s", self.service.service_uuid)
        self.logger.info(
            "RFID query characteristic UUID: %s",
            self.service.rfid_query_characteristic.uuid,
        )
        self.logger.info(
            "Object response characteristic UUID: %s",
            self.service.object_response_characteristic.uuid,
        )
        self.logger.info(
            "BlueZ BLE advertising placeholder active. "
            "Replace with concrete D-Bus GATT registration when targeting hardware."
        )

    async def handle_rfid(self, rfid_id: str) -> dict:
        response = self.service.handle_rfid_query(rfid_id, self._lookup)
        self.logger.info("Incoming RFID: %s", rfid_id)
        self.logger.info("Outgoing JSON: %s", to_pretty_json(response))
        return response

    async def run_mock_cli(self) -> None:
        self.logger.info("Mock mode enabled. Type an RFID value, or 'quit' to stop.")
        while True:
            rfid_id = (await asyncio.to_thread(input, "RFID> ")).strip()
            if not rfid_id:
                continue
            if rfid_id.lower() in {"quit", "exit"}:
                self.logger.info("Shutting down mock BLE server.")
                return
            await self.handle_rfid(rfid_id)

    async def wait_forever(self) -> None:
        await asyncio.Event().wait()

    def _lookup(self, rfid_id: str) -> dict:
        storage_info = self.store.lookup(rfid_id)
        if storage_info is None:
            return object_not_found_response(rfid_id)
        return object_found_response(storage_info)
