"""BLE server facade for the Ubuntu BlueZ peripheral."""

import asyncio

from ..database.object_store import ObjectStore
from ..utils.logger import get_logger


class BLEWarehouseServer:
    """Runs the BlueZ BLE peripheral and optional manual test CLI."""

    def __init__(self, store: ObjectStore) -> None:
        self.store = store
        self.logger = get_logger()
        self.peripheral = None

    async def start(self) -> None:
        from .bluez_peripheral import BlueZWarehousePeripheral

        self.logger.info("Initializing BlueZ BLE peripheral...")
        self.peripheral = BlueZWarehousePeripheral(self.store, logger=self.logger)
        self.peripheral.start()

    def handle_rfid(self, rfid_id: str) -> dict:
        if self.peripheral is None:
            raise RuntimeError("BlueZ peripheral has not been started yet")
        return self.peripheral.handle_rfid(rfid_id)

    async def run_mock_cli(self) -> None:
        self.logger.info("Mock mode enabled. Type an RFID value, or 'quit' to stop.")
        while True:
            rfid_id = (await asyncio.to_thread(input, "RFID> ")).strip()
            if not rfid_id:
                continue
            if rfid_id.lower() in {"quit", "exit"}:
                self.logger.info("Shutting down mock BLE server.")
                return
            self.handle_rfid(rfid_id)

    async def wait_forever(self) -> None:
        await asyncio.Event().wait()
