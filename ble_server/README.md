# BLE Warehouse Server (Ubuntu)

This project provides a BlueZ GATT peripheral for an ESP32 BLE client. It advertises automatically at startup, accepts RFID IDs, and returns object information JSON from a local database.

## Project Structure

```text
ble_server/
├── main.py
├── requirements.txt
├── README.md
├── ble/
│   ├── server.py
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
sudo apt install -y bluetooth bluez python3 python3-venv python3-dbus python3-gi
sudo systemctl enable --now bluetooth
```

2. Create and activate a virtual environment:

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r ble_server/requirements.txt
```

The BLE server depends on the system `dbus` and `gi` packages installed by `apt`.

If you already created the virtual environment without `--system-site-packages`, recreate it after installing the Ubuntu packages above. The `dbus` module is provided by the system Python packages, not by `pip`.

## BLE Permissions Notes

- Run as a user with access to Bluetooth services.
- If needed for low-level BLE access, run with elevated permissions:

```bash
sudo -E python3 -m ble_server.main
```

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'dbus'`, install the missing system packages and recreate the venv:

```bash
sudo apt update
sudo apt install -y bluetooth bluez python3-dbus python3-gi
rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r ble_server/requirements.txt
```

## Run the Server

Auto-advertising BLE peripheral mode:

```bash
python3 -m ble_server.main
```

Interactive mock mode for manual RFID input:

```bash
python3 -m ble_server.main --mock-cli
```

## Expected BLE Workflow

1. Server initializes the object database.
2. Server registers a BlueZ GATT service with the fixed UUIDs.
3. Server advertises automatically on startup.
4. ESP32 scans, connects, and writes the RFID ID to the query characteristic.
5. Server looks up `database/objects.json`.
6. Server updates the response characteristic with JSON and notifies subscribed clients.

## Example Messages

Incoming RFID:

```text
93A7C412
```

Outgoing JSON:

```json
{
  // "objectID": "A12",
  "objectName": "Precision Bearings BT",
  // "status": "Available",
  "location": "Shelf 3BT"
}
```
