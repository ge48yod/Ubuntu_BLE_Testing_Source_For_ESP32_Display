# BLE Warehouse Server (Ubuntu)

This project provides a BlueZ GATT peripheral for ESP32 BLE clients. It advertises automatically at startup, accepts RFID IDs, and returns object information JSON from a local database on a per-device basis.

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
6. Server updates the response characteristic with JSON for the device that sent the RFID.
7. Multiple clients can write different RFID values at the same time without overwriting each other's response payload.

## Example Messages

Incoming RFID examples:

```text
93A7C412
93A7C413
93A7C414
```

Outgoing JSON examples:

```json
{
  "rfidID": "93A7C412",
  "objectName": "Precision Bearings BT",
  // "status": "Available",
  "location": "Shelf 3BT"
}

{
  "rfidID": "93A7C413",
  "objectName": "Hydraulic Seals BT",
  "location": "Shelf 4BT"
}

{
  "rfidID": "93A7C414",
  "objectName": "Torque Sensor BT",
  "location": "Shelf 5BT"
}
```

## Code Framework Overview

This section is meant for developers who want to understand the code base quickly.

### Main flow

1. `ble_server/main.py` is the entry point.
2. `ble_server/database/object_store.py` loads `ble_server/database/objects.json` into memory.
3. `ble_server/ble/server.py` creates the higher-level server wrapper.
4. `ble_server/ble/bluez_peripheral.py` registers the BlueZ GATT objects and starts advertising.
5. The ESP32 writes an RFID value to the query characteristic.
6. The server looks up that RFID in the database and stores JSON for the requesting Bluetooth device.
7. Each connected device can read back its own response without clobbering other clients' payloads.

### Bluetooth terms used in the code

- GATT: The Bluetooth profile used here for exchanging structured data after a device connects.
- Service: A container for related characteristics. This project exposes one service for the warehouse lookup workflow.
- Characteristic: A value inside a service. One characteristic accepts RFID input, and one characteristic returns JSON output.
- Advertisement: The small broadcast message the peripheral sends out so nearby Bluetooth scanners can discover it before connecting.

### What to read first

If you are extending the behavior, start with these files in order:

- [ble_server/main.py](main.py)
- [ble_server/ble/server.py](ble/server.py)
- [ble_server/ble/bluez_peripheral.py](ble/bluez_peripheral.py)
- [ble_server/database/object_store.py](database/object_store.py)
- [ble_server/mock/mock_responses.py](mock/mock_responses.py)

### Common extension points

- Add or change RFID-to-object data in `ble_server/database/objects.json`.
- Adjust the JSON payload shape in `ble_server/mock/mock_responses.py`.
- Change the BLE UUIDs in `ble_server/ble/uuids.py`.
- Modify startup or mock CLI behavior in `ble_server/ble/server.py` and `ble_server/main.py`.
