import unittest

from ble_server.database.object_store import default_store
from ble_server.mock.mock_responses import object_not_found_response


class ObjectLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = default_store()

    def test_lookup_existing_rfid(self) -> None:
        examples = {
            "93A7C412": "Shelf 3BT",
            "93A7C413": "Shelf 4BT",
            "93A7C414": "Shelf 5BT",
        }

        for rfid_id, expected_location in examples.items():
            info = self.store.lookup(rfid_id)
            self.assertIsNotNone(info)
            assert info is not None
            self.assertEqual(info.to_dict()["location"], expected_location)

    def test_lookup_unknown_rfid(self) -> None:
        info = self.store.lookup("DOES_NOT_EXIST")
        self.assertIsNone(info)

    def test_not_found_response_contains_rfid(self) -> None:
        payload = object_not_found_response("DOES_NOT_EXIST")
        self.assertEqual(payload["rfidID"], "DOES_NOT_EXIST")

    def test_found_response_has_expected_shape(self) -> None:
        info = self.store.lookup("93A7C412")
        self.assertIsNotNone(info)
        assert info is not None
        payload = info.to_dict()
        self.assertEqual(payload["objectName"], "Precision Bearings BT")
        self.assertNotIn("rfidID", payload)


if __name__ == "__main__":
    unittest.main()
