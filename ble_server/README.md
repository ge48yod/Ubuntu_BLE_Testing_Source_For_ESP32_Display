# BLE Mock Warehouse Server (Ubuntu)

This project provides a Python BLE mock backend for an ESP32 BLE client. It accepts RFID IDs and returns object information JSON from a local mock database.

## Project Structure

```text
ble_server/
├── main.py
├── requirements.txt
├── README.md
├── ble/
│   ├── server.py
│   ├── service.py
│   ├── characteristics.py
│   └── uuids.py
├── database/
│   ├── object_store.py
│   └── objects.json
├── models/
│   └── storage_info.py
├── mock/
│   └── mock_responses.py
├── utils/
│   ├── json_utils.py
│   └── logger.py
└── tests/
    └── test_lookup.py
```

## Ubuntu Setup

1. Ensure Bluetooth is enabled and BlueZ is installed:

```bash
sudo apt update
sudo apt install -y bluetooth bluez python3 python3-venv
sudo systemctl enable --now bluetooth
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r ble_server/requirements.txt
```

## BLE Permissions Notes

- Run as a user with access to Bluetooth services.
- If needed for low-level BLE access, run with elevated permissions:

```bash
sudo -E python3 -m ble_server.main
```

## Run the Server

Interactive mock mode (recommended for local testing without ESP32):

```bash
python3 -m ble_server.main
```

Non-interactive mode (keeps server process alive):

```bash
python3 -m ble_server.main --no-mock-cli
```

## Expected BLE Workflow

1. Server initializes mock database.
2. Server initializes BLE service and characteristic UUIDs.
3. BLE advertising placeholder starts (ready for BlueZ GATT extension).
4. ESP32 client writes RFID ID to RFID query characteristic.
5. Server looks up `database/objects.json`.
6. Server writes JSON to object response characteristic.

## Example Messages

Incoming RFID:

```text
93A7C412
```

Outgoing JSON:

```json
{
  "objectID": "A12",
  "objectName": "Precision Bearings",
  "status": "Available",
  "location": "Shelf 3"
}
```
