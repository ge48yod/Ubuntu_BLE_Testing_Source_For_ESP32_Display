"""Entrypoint for the Ubuntu BLE mock warehouse server."""

import argparse
import asyncio

from ble_server.ble.server import BLEWarehouseServer
from ble_server.database.object_store import default_store
from ble_server.utils.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mock BLE warehouse server for ESP32 clients")
    parser.add_argument(
        "--mock-cli",
        action="store_true",
        help="Run an interactive RFID input mode for manual testing",
    )
    return parser.parse_args()


async def run_server(mock_cli_enabled: bool) -> None:
    logger = get_logger()
    logger.info("Initializing mock object database...")
    store = default_store()

    logger.info("Initializing BLE service...")
    server = BLEWarehouseServer(store)
    await server.start()

    logger.info("BLE server running and waiting for RFID requests...")
    if mock_cli_enabled:
        await server.run_mock_cli()
    else:
        await server.wait_forever()


def main() -> None:
    args = parse_args()
    asyncio.run(run_server(args.mock_cli))


if __name__ == "__main__":
    main()
