"""BlueZ GATT peripheral for the warehouse mock backend."""

from __future__ import annotations

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from ..database.object_store import ObjectStore
from ..mock.mock_responses import object_found_response, object_not_found_response
from ..utils.json_utils import to_json_string
from ..utils.logger import get_logger
from .uuids import (
    OBJECT_RESPONSE_CHARACTERISTIC_UUID,
    RFID_QUERY_CHARACTERISTIC_UUID,
    SERVICE_UUID,
)

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


class Application(dbus.service.Object):
    """org.bluez.GattApplication1 implementation."""

    def __init__(self, bus: dbus.Bus) -> None:
        self.path = "/"
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self) -> dbus.ObjectPath:
        return dbus.ObjectPath(self.path)

    def add_service(self, service: "Service") -> None:
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            for characteristic in service.get_characteristics():
                response[characteristic.get_path()] = characteristic.get_properties()
        return response


class Service(dbus.service.Object):
    """org.bluez.GattService1 implementation."""

    PATH_BASE = "/org/bluez/warehouse/service"

    def __init__(self, bus: dbus.Bus, index: int, uuid: str, primary: bool) -> None:
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.uuid = uuid
        self.primary = primary
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_SERVICE_IFACE: {
                "UUID": self.uuid,
                "Primary": self.primary,
                "Characteristics": dbus.Array(self.get_characteristic_paths(), signature="o"),
            }
        }

    def get_path(self) -> dbus.ObjectPath:
        return dbus.ObjectPath(self.path)

    def add_characteristic(self, characteristic: "Characteristic") -> None:
        self.characteristics.append(characteristic)

    def get_characteristics(self):
        return self.characteristics

    def get_characteristic_paths(self):
        return [characteristic.get_path() for characteristic in self.characteristics]

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_SERVICE_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_SERVICE_IFACE]


class Characteristic(dbus.service.Object):
    """org.bluez.GattCharacteristic1 implementation."""

    def __init__(self, bus: dbus.Bus, index: int, uuid: str, flags: list[str], service: Service) -> None:
        self.path = f"{service.path}/char{index}"
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.flags = flags
        self.value = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_CHRC_IFACE: {
                "Service": self.service.get_path(),
                "UUID": self.uuid,
                "Flags": self.flags,
            }
        }

    def get_path(self) -> dbus.ObjectPath:
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != GATT_CHRC_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[GATT_CHRC_IFACE]

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options):
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature="aya{sv}")
    def WriteValue(self, value, options):
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StartNotify(self):
        raise NotSupportedException()

    @dbus.service.method(GATT_CHRC_IFACE)
    def StopNotify(self):
        raise NotSupportedException()

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass


class Advertisement(dbus.service.Object):
    """org.bluez.LEAdvertisement1 implementation."""

    PATH_BASE = "/org/bluez/warehouse/advertisement"

    def __init__(self, bus: dbus.Bus, index: int, advertising_type: str) -> None:
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.ad_type = advertising_type
        self.service_uuids = []
        self.local_name = None
        self.include_tx_power = True
        dbus.service.Object.__init__(self, bus, self.path)

    def add_service_uuid(self, uuid: str) -> None:
        self.service_uuids.append(uuid)

    def add_local_name(self, name: str) -> None:
        self.local_name = dbus.String(name)

    def get_properties(self):
        properties = {
            "Type": self.ad_type,
            "ServiceUUIDs": dbus.Array(self.service_uuids, signature="s"),
        }
        if self.local_name is not None:
            properties["LocalName"] = self.local_name
        if self.include_tx_power:
            properties["Includes"] = dbus.Array(["tx-power"], signature="s")
        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self) -> dbus.ObjectPath:
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface != LE_ADVERTISEMENT_IFACE:
            raise InvalidArgsException()
        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE)
    def Release(self):
        return


class WarehouseResponseCharacteristic(Characteristic):
    """Characteristic that exposes the JSON lookup result."""

    def __init__(self, bus: dbus.Bus, index: int, service: Service) -> None:
        super().__init__(bus, index, OBJECT_RESPONSE_CHARACTERISTIC_UUID, ["read", "notify"], service)
        self.value = b""
        self.notifying = False

    def ReadValue(self, options):
        return [dbus.Byte(byte) for byte in self.value]

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": [dbus.Byte(byte) for byte in self.value]}, [])

    def StopNotify(self):
        self.notifying = False

    def set_payload(self, payload: dict) -> None:
        self.value = to_json_string(payload).encode("utf-8")
        if self.notifying:
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": [dbus.Byte(byte) for byte in self.value]}, [])


class WarehouseRFIDQueryCharacteristic(Characteristic):
    """Write-only characteristic used by the ESP32 client to submit RFID values."""

    def __init__(self, bus: dbus.Bus, index: int, service: Service, peripheral: "BlueZWarehousePeripheral") -> None:
        super().__init__(bus, index, RFID_QUERY_CHARACTERISTIC_UUID, ["write"], service)
        self.peripheral = peripheral

    def WriteValue(self, value, options):
        rfid_id = bytes(value).decode("utf-8").strip()
        if not rfid_id:
            raise FailedException("Empty RFID payload")
        self.peripheral.handle_rfid(rfid_id)


class WarehouseService(Service):
    def __init__(self, bus: dbus.Bus, peripheral: "BlueZWarehousePeripheral") -> None:
        super().__init__(bus, 0, SERVICE_UUID, True)
        self.response_characteristic = WarehouseResponseCharacteristic(bus, 0, self)
        self.query_characteristic = WarehouseRFIDQueryCharacteristic(bus, 1, self, peripheral)
        self.add_characteristic(self.response_characteristic)
        self.add_characteristic(self.query_characteristic)


class WarehouseAdvertisement(Advertisement):
    def __init__(self, bus: dbus.Bus) -> None:
        super().__init__(bus, 0, "peripheral")
        self.add_service_uuid(SERVICE_UUID)
        self.add_local_name("Ubuntu Warehouse BLE")


class BlueZWarehousePeripheral:
    """Registers a BlueZ GATT application and advertises it automatically."""

    def __init__(self, store: ObjectStore, logger=None) -> None:
        self.store = store
        self.logger = logger or get_logger()
        self.bus = None
        self.mainloop = None
        self.application = None
        self.advertisement = None
        self.service = None

    def start(self) -> None:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        adapter_path = self._find_adapter(self.bus)
        if adapter_path is None:
            raise RuntimeError("BlueZ adapter with GATT and advertising support was not found")

        adapter_object = self.bus.get_object(BLUEZ_SERVICE_NAME, adapter_path)
        adapter_props = dbus.Interface(adapter_object, DBUS_PROP_IFACE)
        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

        gatt_manager = dbus.Interface(adapter_object, GATT_MANAGER_IFACE)
        advertising_manager = dbus.Interface(adapter_object, LE_ADVERTISING_MANAGER_IFACE)

        self.application = Application(self.bus)
        self.service = WarehouseService(self.bus, self)
        self.application.add_service(self.service)
        self.advertisement = WarehouseAdvertisement(self.bus)

        self.mainloop = GLib.MainLoop()

        from threading import Thread

        Thread(target=self.mainloop.run, daemon=True).start()

        self._register_gatt_application(gatt_manager)
        self._register_advertisement(advertising_manager)

        self.logger.info("BlueZ GATT service registered and advertising.")
        self.logger.info("Service UUID: %s", SERVICE_UUID)
        self.logger.info("RFID query characteristic UUID: %s", RFID_QUERY_CHARACTERISTIC_UUID)
        self.logger.info("Object response characteristic UUID: %s", OBJECT_RESPONSE_CHARACTERISTIC_UUID)

    def stop(self) -> None:
        if self.mainloop is not None and self.mainloop.is_running():
            self.mainloop.quit()

    def handle_rfid(self, rfid_id: str) -> dict:
        storage_info = self.store.lookup(rfid_id)
        if storage_info is None:
            response = object_not_found_response(rfid_id)
        else:
            response = object_found_response(storage_info)

        self.logger.info("Incoming RFID: %s", rfid_id)
        self.logger.info("Outgoing JSON: %s", to_json_string(response))

        if self.service is not None:
            self.service.response_characteristic.set_payload(response)

        return response

    def _register_gatt_application(self, gatt_manager) -> None:
        self._register_with_manager(
            "GATT application",
            self.application.get_path(),
            lambda reply_handler, error_handler: gatt_manager.RegisterApplication(
                self.application.get_path(), {}, reply_handler=reply_handler, error_handler=error_handler
            ),
        )

    def _register_advertisement(self, advertising_manager) -> None:
        self._register_with_manager(
            "advertisement",
            self.advertisement.get_path(),
            lambda reply_handler, error_handler: advertising_manager.RegisterAdvertisement(
                self.advertisement.get_path(), {}, reply_handler=reply_handler, error_handler=error_handler
            ),
        )

    def _register_with_manager(self, label: str, path: dbus.ObjectPath, register_call) -> None:
        from threading import Event

        done = Event()
        errors: list[Exception] = []

        def reply_handler(*_args):
            done.set()

        def error_handler(error):
            errors.append(RuntimeError(f"Failed to register {label}: {error}"))
            done.set()

        register_call(reply_handler, error_handler)
        if not done.wait(timeout=10):
            raise RuntimeError(f"Timed out while registering {label} at {path}")
        if errors:
            raise errors[0]

    @staticmethod
    def _find_adapter(bus: dbus.Bus):
        remote_object_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
        objects = remote_object_manager.GetManagedObjects()
        for path, interfaces in objects.items():
            if GATT_MANAGER_IFACE in interfaces and LE_ADVERTISING_MANAGER_IFACE in interfaces:
                return path
        return None
