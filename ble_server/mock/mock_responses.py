"""Response builders for known and unknown RFID lookups."""

from ..models.storage_info import StorageInfo


def object_found_response(storage_info: StorageInfo) -> dict:
    return storage_info.to_dict()


def object_not_found_response(rfid_id: str) -> dict:
    return {
        "objectName": "Not Found",
        "location": "N/A",
        "rfidID": rfid_id,
    }
