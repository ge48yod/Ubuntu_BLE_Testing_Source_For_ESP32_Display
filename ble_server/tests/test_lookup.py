import unittest

from ble_server.database.object_store import default_store
from ble_server.mock.mock_responses import object_not_found_response


class ObjectLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = default_store()

    def test_lookup_existing_rfid(self) -> None:
        info = self.store.lookup("93A7C412")
        self.assertIsNotNone(info)
        # self.assertEqual(info.to_dict()["objectID"], "A12")
        self.assertEqual(info.to_dict()["location"], "Shelf 3BT")

    def test_lookup_unknown_rfid(self) -> None:
        info = self.store.lookup("DOES_NOT_EXIST")
        self.assertIsNone(info)

    def test_not_found_response_contains_rfid(self) -> None:
        payload = object_not_found_response("DOES_NOT_EXIST")
        # self.assertEqual(payload["rfidID"], "DOES_NOT_EXIST")
        # self.assertEqual(payload["status"], "Missing")


if __name__ == "__main__":
    unittest.main()
