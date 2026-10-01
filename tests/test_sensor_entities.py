"""Regression tests for regular and experimental sensor entities."""

from __future__ import annotations

import importlib.util
import copy
import itertools
from pathlib import Path
from types import SimpleNamespace
import sys
import types
import unittest
from unittest.mock import AsyncMock


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "custom_components" / "weishaupt_wtc_lan"


def load_module(module_name: str, file_path: Path):
    """Load a package module from a file."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


homeassistant_pkg = types.ModuleType("homeassistant")
homeassistant_pkg.__path__ = []
sys.modules.setdefault("homeassistant", homeassistant_pkg)

components_pkg = types.ModuleType("homeassistant.components")
components_pkg.__path__ = []
sys.modules.setdefault("homeassistant.components", components_pkg)

sensor_component = types.ModuleType("homeassistant.components.sensor")


class SensorEntity:
    """Minimal sensor entity stub."""


class SensorDeviceClass:
    """Return enum member names as strings."""

    def __getattr__(self, name: str) -> str:
        return name


class SensorStateClass:
    """Return enum member names as strings."""

    def __getattr__(self, name: str) -> str:
        return name


sensor_component.SensorEntity = SensorEntity
sensor_component.SensorDeviceClass = SensorDeviceClass()
sensor_component.SensorStateClass = SensorStateClass()
sys.modules["homeassistant.components.sensor"] = sensor_component

select_component = types.ModuleType("homeassistant.components.select")


class SelectEntity:
    """Minimal select entity stub."""


select_component.SelectEntity = SelectEntity
sys.modules["homeassistant.components.select"] = select_component

number_component = types.ModuleType("homeassistant.components.number")
number_component.NumberEntity = type("NumberEntity", (), {})
number_component.NumberMode = SimpleNamespace(SLIDER="slider")
sys.modules["homeassistant.components.number"] = number_component
button_component = types.ModuleType("homeassistant.components.button")
button_component.ButtonEntity = type("ButtonEntity", (), {})
sys.modules["homeassistant.components.button"] = button_component

config_entries = types.ModuleType("homeassistant.config_entries")
config_entries.ConfigEntry = object
sys.modules["homeassistant.config_entries"] = config_entries

core = types.ModuleType("homeassistant.core")
core.HomeAssistant = object
core.callback = lambda func: func
sys.modules["homeassistant.core"] = core

const = types.ModuleType("homeassistant.const")
const.PERCENTAGE = "%"
const.UnitOfEnergy = SimpleNamespace(KILO_WATT_HOUR="kWh")
const.UnitOfPower = SimpleNamespace(KILO_WATT="kW")
const.UnitOfPressure = SimpleNamespace(BAR="bar")
const.UnitOfTemperature = SimpleNamespace(CELSIUS="C")
const.UnitOfTime = SimpleNamespace(HOURS="h")
sys.modules["homeassistant.const"] = const

helpers_pkg = types.ModuleType("homeassistant.helpers")
helpers_pkg.__path__ = []
sys.modules["homeassistant.helpers"] = helpers_pkg

device_registry_module = types.ModuleType("homeassistant.helpers.device_registry")
device_registry_module.DeviceInfo = dict
sys.modules["homeassistant.helpers.device_registry"] = device_registry_module
helpers_pkg.device_registry = device_registry_module

entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
entity_platform.AddEntitiesCallback = object
sys.modules["homeassistant.helpers.entity_platform"] = entity_platform

entity_module = types.ModuleType("homeassistant.helpers.entity")
entity_module.EntityCategory = SimpleNamespace(DIAGNOSTIC="diagnostic", CONFIG="config")
sys.modules["homeassistant.helpers.entity"] = entity_module

update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")


class CoordinatorEntity:
    """Minimal coordinator entity stub."""

    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator) -> None:
        self.coordinator = coordinator

    @property
    def available(self) -> bool:
        return True


update_coordinator.CoordinatorEntity = CoordinatorEntity
sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator

custom_components_pkg = types.ModuleType("custom_components")
custom_components_pkg.__path__ = [str(REPO_ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components_pkg)

integration_pkg = types.ModuleType("custom_components.weishaupt_wtc_lan")
integration_pkg.__path__ = [str(PACKAGE_ROOT)]
sys.modules.setdefault("custom_components.weishaupt_wtc_lan", integration_pkg)

load_module("custom_components.weishaupt_wtc_lan.const", PACKAGE_ROOT / "const.py")
load_module("custom_components.weishaupt_wtc_lan.parsing", PACKAGE_ROOT / "parsing.py")
sensors = load_module(
    "custom_components.weishaupt_wtc_lan.sensors", PACKAGE_ROOT / "sensors.py"
)
heating_circuits = load_module(
    "custom_components.weishaupt_wtc_lan.heating_circuits",
    PACKAGE_ROOT / "heating_circuits.py",
)

coordinator_module = types.ModuleType("custom_components.weishaupt_wtc_lan.coordinator")
coordinator_module.WeishauptDataUpdateCoordinator = object
sys.modules["custom_components.weishaupt_wtc_lan.coordinator"] = coordinator_module

sensor = load_module(
    "custom_components.weishaupt_wtc_lan.sensor", PACKAGE_ROOT / "sensor.py"
)
select_platform = load_module(
    "custom_components.weishaupt_wtc_lan.select", PACKAGE_ROOT / "select.py"
)
number_platform = load_module(
    "custom_components.weishaupt_wtc_lan.number", PACKAGE_ROOT / "number.py"
)
button_platform = load_module(
    "custom_components.weishaupt_wtc_lan.button", PACKAGE_ROOT / "button.py"
)


def sensor_by_key(key: str):
    """Return a sensor definition by key."""
    return next(sensor_def for sensor_def in sensors.ALL_SENSORS if sensor_def.key == key)


class DeviceRegistry:
    """Minimal device registry capturing created devices."""

    def __init__(self) -> None:
        self.created: list[dict] = []
        self.devices: dict[tuple[str, tuple[str, str]], SimpleNamespace] = {}

    def async_get_or_create(self, **kwargs):
        assert "via_device" not in kwargs
        owner = kwargs["config_entry_id"]
        identifier = next(iter(kwargs["identifiers"]))
        key = (owner, identifier)
        parent_id = kwargs.get("via_device_id")
        if parent_id is not None:
            assert isinstance(parent_id, str)
            assert any(
                device.id == parent_id and device.config_entry_id == owner
                for device in self.devices.values()
            )
        if key not in self.devices:
            self.created.append(kwargs)
            self.devices[key] = SimpleNamespace(
                id=f"registry-{len(self.devices)}",
                config_entry_id=owner,
                area_id=None,
                name_by_user=None,
                disabled_by=None,
                **{k: v for k, v in kwargs.items() if k != "config_entry_id"},
            )
        device = self.devices[key]
        for field, value in kwargs.items():
            setattr(device, field, value)
        return device

    def async_get_device_by_identifier(self, identifier, config_entry_id):
        return self.devices.get((config_entry_id, identifier))


class SensorEntityTests(unittest.IsolatedAsyncioTestCase):
    """Test regular and experimental sensor behavior."""

    def setUp(self) -> None:
        self.registry = DeviceRegistry()
        sensor.dr.async_get = lambda hass: self.registry

    def _migration_fixture(self):
        definitions = heating_circuits.build_sensor_definitions(
            [1, 2, 3], {"system", "wtc", "ww"}
        )
        definitions.append(next(
            item for item in sensors.NETWORK_SENSORS
            if item.key == "network_ip_address"
        ))
        register = sensors.EXPERIMENTAL_WTC_REGISTERS[0]
        data = {
            "sg_aussentemperatur": {"value_int": 125, "value_hex": "007d"},
            "wtc_anlagendruck": {"value_int": 149, "value_hex": "0095"},
            "sg_systembetriebsart": {"value_int": 3, "value_hex": "03"},
            "sg_betriebsart_hk1_vorgabe": {"value_int": 2, "value_hex": "02"},
            "hk_betriebsart_vorgabe": {"value_int": 2, "value_hex": "02"},
            "hk3_betriebsart_vorgabe": {"value_int": 2, "value_hex": "02"},
            "sg_wwsolltemperatur_normal": {"value_int": 550, "value_hex": "0226"},
            "sg_wwsolltemperatur_absenk": {"value_int": 400, "value_hex": "0190"},
            "network_ip_address": {"value_int": 0xC0A8012A, "value_hex": "c0a8012a"},
            register.key: {"value_int": 0, "value_hex": "00" * register.vs},
        }
        coordinator = SimpleNamespace(
            sensor_definitions=definitions,
            experimental_wtc_registers=[register],
            extended_experimental_wtc_registers=[],
            heating_circuit_names={1: "Custom HK1", 2: "Custom HK2", 3: "Custom HK3"},
            data=data,
            async_enqueue_write=AsyncMock(),
        )
        entry = SimpleNamespace(
            entry_id="entry-123", data={"host": "wem-sg.local"},
            options={"scan_interval": 60, "hk1_name": "Custom HK1"},
        )
        return coordinator, entry

    async def _add_migration_entities(self, coordinator, entry, platforms):
        hass = SimpleNamespace(data={"weishaupt_wtc_lan": {entry.entry_id: coordinator}})
        added = []
        for platform in platforms:
            def add_entities(entities):
                for entity in entities:
                    info = entity.device_info
                    self.assertNotIn("via_device", info)
                    device = self.registry.async_get_or_create(
                        config_entry_id=entry.entry_id, **info
                    )
                    if info["identifiers"] == {sensor._system_device_identifier(entry.entry_id)}:
                        self.assertNotIn("via_device_id", info)
                    else:
                        self.assertEqual(info["via_device_id"], coordinator.system_device_id)
                        self.assertNotEqual(device.id, coordinator.system_device_id)
                    added.append(entity)
            await platform.async_setup_entry(hass, entry, add_entities)
        return added

    async def test_first_setup_registers_real_parent_id_in_every_platform_order(self):
        """Any platform order must not depend on sensor being first."""
        for platforms in itertools.permutations(
            [sensor, select_platform, number_platform, button_platform]
        ):
            with self.subTest(order=[item.__name__ for item in platforms]):
                self.registry = DeviceRegistry()
                coordinator, entry = self._migration_fixture()
                entities = await self._add_migration_entities(coordinator, entry, platforms)
                root = self.registry.async_get_device_by_identifier(
                    ("weishaupt_wtc_lan", "entry-123_sg"), entry.entry_id
                )
                self.assertEqual(coordinator.system_device_id, root.id)
                self.assertNotEqual(root.id, "entry-123_sg")
                unique_ids = [entity._attr_unique_id for entity in entities]
                self.assertEqual(len(unique_ids), len(set(unique_ids)))
                self.assertEqual(len(self.registry.devices), 8)

    async def test_existing_devices_and_entities_survive_reload_with_user_settings(self):
        """Reuse registry IDs, configured names and entity settings across reloads."""
        coordinator, entry = self._migration_fixture()
        # Simulate HA's persisted registry, including a conflicting identifier
        # owned by another ConfigEntry.
        foreign = self.registry.async_get_or_create(
            config_entry_id="foreign-entry",
            identifiers={("weishaupt_wtc_lan", "entry-123_sg")},
        )
        root = self.registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={("weishaupt_wtc_lan", "entry-123_sg")},
        )
        for suffix in ("hk1", "hk", "hk3", "ww", "wtc", "network", "wtc_experimental"):
            self.registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={("weishaupt_wtc_lan", f"entry-123_{suffix}")},
                via_device_id=root.id,
            )
        for device in self.registry.devices.values():
            device.area_id = "boiler-room"
            device.name_by_user = "User device name"
            device.disabled_by = "user"
        registry_before = copy.deepcopy(self.registry.devices)
        config_before = copy.deepcopy((entry.data, entry.options))
        entities_before = {
            "entry-123_wtc_anlagendruck": {
                "entity_id": "sensor.existing_pressure", "disabled_by": "user",
                "name": "Custom pressure", "device_id": self.registry.devices[
                    (entry.entry_id, ("weishaupt_wtc_lan", "entry-123_wtc"))
                ].id,
            },
            "entry-123_sg_wwsolltemperatur_normal_number": {
                "entity_id": "number.existing_ww_target", "disabled_by": None,
                "name": "Custom target", "device_id": self.registry.devices[
                    (entry.entry_id, ("weishaupt_wtc_lan", "entry-123_ww"))
                ].id,
            },
        }
        entity_registry = copy.deepcopy(entities_before)
        expected_devices = len(self.registry.devices)
        for _ in range(2):
            # Reload creates a new coordinator, but keeps entry and registry.
            coordinator, _unused_entry = self._migration_fixture()
            entities = await self._add_migration_entities(
                coordinator, entry,
                [number_platform, button_platform, select_platform, sensor],
            )
            self.assertEqual(coordinator.system_device_id, root.id)
            self.assertNotEqual(coordinator.system_device_id, foreign.id)
            self.assertEqual(len(self.registry.devices), expected_devices)
            by_unique_id = {entity._attr_unique_id: entity for entity in entities}
            self.assertEqual(by_unique_id["entry-123_wtc_anlagendruck"].native_value, 1.49)
            self.assertEqual(by_unique_id["entry-123_sg_aussentemperatur"].native_value, 12.5)
            self.assertEqual(by_unique_id["entry-123_sg_systembetriebsart"].current_option, "Automatik")
            for key in (
                "sg_betriebsart_hk1_vorgabe",
                "hk_betriebsart_vorgabe_select",
                "hk3_betriebsart_vorgabe_select",
            ):
                self.assertEqual(by_unique_id[f"entry-123_{key}"].current_option, "Zeitprogramm 1")
            self.assertEqual(by_unique_id["entry-123_sg_wwsolltemperatur_normal_number"].native_value, 55.0)
            self.assertEqual(by_unique_id["entry-123_sg_wwsolltemperatur_absenk_number"].native_value, 40.0)
            for entity in entities:
                unique_id = entity._attr_unique_id
                device = self.registry.async_get_device_by_identifier(
                    next(iter(entity.device_info["identifiers"])), entry.entry_id
                )
                if unique_id in entity_registry:
                    self.assertEqual(entity_registry[unique_id]["device_id"], device.id)
                else:
                    entity_registry[unique_id] = {
                        "entity_id": f"sensor.{unique_id}", "device_id": device.id,
                    }
            for key, original in entities_before.items():
                self.assertEqual(entity_registry[key], original)
            await by_unique_id["entry-123_sg_systembetriebsart"].async_select_option("Sommer")
            await by_unique_id["entry-123_sg_wwsolltemperatur_normal_number"].async_set_native_value(56.0)
            await by_unique_id["entry-123_sg_warmwasser_push"].async_press()
            self.assertEqual(
                [(args[0].key, args[1]) for args, _kwargs in coordinator.async_enqueue_write.call_args_list],
                [("sg_systembetriebsart", 2), ("sg_wwsolltemperatur_normal", 560), ("sg_warmwasser_push", 1)],
            )
        for key, old in registry_before.items():
            device = self.registry.devices[key]
            self.assertEqual(device.id, old.id)
            self.assertEqual(device.area_id, old.area_id)
            self.assertEqual(device.name_by_user, old.name_by_user)
            self.assertEqual(device.disabled_by, old.disabled_by)
            self.assertEqual(getattr(device, "via_device_id", None), getattr(old, "via_device_id", None))
        self.assertEqual((entry.data, entry.options), config_before)

    def test_confirmed_wtc_frames_render_valid_zero_and_counter_values(self) -> None:
        """Confirmed WTC raw values should render expected HA states."""
        keys_and_expected = {
            "wtc_anlagendruck": (149, "0095", 1.49),
            "wtc_kesseltemperatur": (402, "0192", 40.2),
            "wtc_volumenstrom_vpt": (0, "0000", 0),
            "wtc_abgastemperatur": (399, "018f", 39.9),
            "wtc_ruecklauftemperatur": (413, "019d", 41.3),
            "wtc_vorlaufsolltemperatur": (80, "0050", 8.0),
            "wtc_brennerstarts_gesamt": (31261, "7a1d", 31261),
            "wtc_betriebsstunden_gesamt": (5604, "15e4", 5604),
        }
        coordinator = SimpleNamespace(
            data={
                key: {"value_int": raw, "value_hex": raw_hex}
                for key, (raw, raw_hex, _expected) in keys_and_expected.items()
            },
        )
        entry = SimpleNamespace(entry_id="entry-123")

        for key, (_raw, _raw_hex, expected) in keys_and_expected.items():
            entity = sensor.WeishauptSensorEntity(
                coordinator=coordinator,
                sensor_def=sensor_by_key(key),
                entry=entry,
            )
            self.assertTrue(entity.available)
            self.assertEqual(entity.native_value, expected)

    def test_experimental_entity_uses_own_device_and_metadata(self) -> None:
        """Experimental sensors should expose raw signed state and metadata."""
        register = next(
            item
            for item in sensors.EXPERIMENTAL_WTC_REGISTERS
            if item.key == "wtc_experimental_09_01_2612_02_02"
        )
        coordinator = SimpleNamespace(
            data={register.key: {"value_int": 597, "value_hex": "0255"}},
            system_device_id="existing-system-registry-id",
        )
        entity = sensor.WeishauptExperimentalWtcSensorEntity(
            coordinator=coordinator,
            register=register,
            entry=SimpleNamespace(entry_id="entry-123"),
        )

        self.assertTrue(entity.available)
        self.assertEqual(entity._attr_unique_id, "entry-123_" + register.key)
        self.assertEqual(entity.native_value, 597)
        self.assertEqual(
            entity.device_info["identifiers"],
            {("weishaupt_wtc_lan", "entry-123_wtc_experimental")},
        )
        attrs = entity.extra_state_attributes
        self.assertEqual(attrs["raw_hex"], "0255")
        self.assertEqual(attrs["raw_unsigned"], 597)
        self.assertEqual(attrs["raw_signed"], 597)
        self.assertEqual(attrs["scaled_x0_1"], 59.7)
        self.assertEqual(attrs["scaled_x0_01"], 5.97)
        self.assertEqual(attrs["mi"], "0x09")
        self.assertEqual(attrs["ox"], "0x2612")
        self.assertEqual(attrs["confidence"], "candidate")
        self.assertEqual(attrs["probable_unit"], "°C")
        self.assertEqual(attrs["probable_scale"], 0.1)

    def test_vpt_power_zero_is_valid_for_adaptive_value_sizes(self) -> None:
        """WTC VPT power should expose raw zero as 0.0 kW for VS=4 and VS=2."""
        sensor_def = sensor_by_key("wtc_waermeleistung_vpt")
        entry = SimpleNamespace(entry_id="entry-123")
        for value_size, raw_hex in ((4, "00000000"), (2, "0000")):
            coordinator = SimpleNamespace(
                data={
                    sensor_def.key: {
                        "value_int": 0,
                        "value_hex": raw_hex,
                    }
                },
            )
            entity = sensor.WeishauptSensorEntity(
                coordinator=coordinator,
                sensor_def=types.SimpleNamespace(
                    **{**sensor_def.__dict__, "vs": value_size}
                ),
                entry=entry,
            )
            self.assertTrue(entity.available)
            self.assertEqual(entity.native_value, 0.0)

    def test_device_date_and_clock_time_are_derived_from_components(self) -> None:
        """Separate device date/time sensors should use existing SG components."""
        coordinator = SimpleNamespace(
            data={
                "sg_uhrzeit_stunden": {"value_int": 17, "value_hex": "11"},
                "sg_uhrzeit_minuten": {"value_int": 25, "value_hex": "19"},
                "sg_datum_tag": {"value_int": 11, "value_hex": "0b"},
                "sg_datum_monat": {"value_int": 6, "value_hex": "06"},
                "sg_datum_jahr": {"value_int": 26, "value_hex": "1a"},
            },
        )
        entry = SimpleNamespace(entry_id="entry-123")

        date_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=sensor_by_key("sg_device_date"),
            entry=entry,
        )
        time_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=sensor_by_key("sg_device_clock_time"),
            entry=entry,
        )

        self.assertTrue(date_entity.available)
        self.assertEqual(date_entity.native_value, "11.06.2026")
        self.assertTrue(time_entity.available)
        self.assertEqual(time_entity.native_value, "17:25")

    def test_device_date_clock_time_and_combined_timestamp_use_corrected_order(self) -> None:
        """Raw date registers should map year/month/day in validated hardware order."""
        self.assertEqual(sensor_by_key("sg_datum_jahr").os, 0x02)
        self.assertEqual(sensor_by_key("sg_datum_monat").os, 0x03)
        self.assertEqual(sensor_by_key("sg_datum_tag").os, 0x04)
        coordinator = SimpleNamespace(
            data={
                "sg_uhrzeit_stunden": {"value_int": 22, "value_hex": "16"},
                "sg_uhrzeit_minuten": {"value_int": 26, "value_hex": "1a"},
                "sg_datum_jahr": {"value_int": 26, "value_hex": "1a"},
                "sg_datum_monat": {"value_int": 6, "value_hex": "06"},
                "sg_datum_tag": {"value_int": 11, "value_hex": "0b"},
            },
        )
        entry = SimpleNamespace(entry_id="entry-123")
        date_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=sensor_by_key("sg_device_date"),
            entry=entry,
        )
        clock_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=sensor_by_key("sg_device_clock_time"),
            entry=entry,
        )
        timestamp_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=sensor_by_key("sg_device_time"),
            entry=entry,
        )

        self.assertEqual(date_entity.native_value, "11.06.2026")
        self.assertEqual(clock_entity.native_value, "22:26")
        self.assertEqual(timestamp_entity.native_value, "2026-06-11T22:26:00+00:00")

    def test_invalid_derived_date_is_unavailable(self) -> None:
        """Invalid component combinations should make the derived date unavailable."""
        entity = sensor.WeishauptSensorEntity(
            coordinator=SimpleNamespace(
                data={
                    "sg_datum_jahr": {"value_int": 26, "value_hex": "1a"},
                    "sg_datum_monat": {"value_int": 2, "value_hex": "02"},
                    "sg_datum_tag": {"value_int": 31, "value_hex": "1f"},
                }
            ),
            sensor_def=sensor_by_key("sg_device_date"),
            entry=SimpleNamespace(entry_id="entry-123"),
        )

        self.assertFalse(entity.available)
        self.assertIsNone(entity.native_value)

    def test_derived_date_time_defaults_and_raw_component_defaults(self) -> None:
        """Derived date/time should be enabled while raw components remain disabled."""
        self.assertTrue(sensor_by_key("sg_device_date").entity_registry_enabled_default)
        self.assertTrue(
            sensor_by_key("sg_device_clock_time").entity_registry_enabled_default
        )
        self.assertFalse(sensor_by_key("sg_device_time").entity_registry_enabled_default)
        for key in (
            "sg_uhrzeit_stunden",
            "sg_uhrzeit_minuten",
            "sg_datum_tag",
            "sg_datum_monat",
            "sg_datum_jahr",
        ):
            self.assertFalse(sensor_by_key(key).entity_registry_enabled_default)

    def test_network_values_render_on_network_device(self) -> None:
        """Network diagnostics should decode static values and use their own device."""
        ip_def = next(
            item for item in sensors.NETWORK_SENSORS if item.key == "network_ip_address"
        )
        host_def = next(
            item for item in sensors.NETWORK_SENSORS if item.key == "network_hostname"
        )
        cert_def = next(
            item
            for item in sensors.NETWORK_SENSORS
            if item.key == "network_certificate_cn"
        )
        mac_def = next(
            item
            for item in sensors.NETWORK_SENSORS
            if item.key == "network_mac_address"
        )
        coordinator = SimpleNamespace(
            data={
                "network_ip_address": {
                    "value_int": 0xC0A8012A,
                    "value_hex": "c0a8012a",
                },
                "network_hostname": {
                    "value_int": 0,
                    "value_hex": "57454d2d534700",
                    "value_string": "WEM-SG",
                },
                "network_certificate_cn": {
                    "value_int": 0,
                    "value_hex": "77656d2e6578616d706c65",
                    "value_string": "wem.example",
                },
                "network_mac_address": {
                    "value_int": 0,
                    "value_hex": "001122aabbcc",
                    "value_string": "00-11-22-AA-BB-CC",
                },
            },
            logical_device_names={"network": "GATEWAY0"},
            system_device_id="existing-system-registry-id",
        )
        entry = SimpleNamespace(
            entry_id="entry-123",
            data={
                "host": "wem-sg.local",
                "username": "admin",
                "password": "secret",
            },
        )

        ip_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=ip_def,
            entry=entry,
        )
        host_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=host_def,
            entry=entry,
        )
        cert_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=cert_def,
            entry=entry,
        )
        mac_entity = sensor.WeishauptSensorEntity(
            coordinator=coordinator,
            sensor_def=mac_def,
            entry=entry,
        )

        self.assertEqual(ip_entity.native_value, "192.168.1.42")
        self.assertEqual(host_entity.native_value, "WEM-SG")
        self.assertEqual(cert_entity.native_value, "wem.example")
        self.assertEqual(mac_entity.native_value, "00-11-22-AA-BB-CC")
        self.assertEqual(
            ip_entity.device_info["identifiers"],
            {("weishaupt_wtc_lan", "entry-123_network")},
        )
        self.assertEqual(ip_entity.device_info["name"], "Weishaupt Systemgerät Netzwerk")
        self.assertEqual(
            ip_entity.device_info["configuration_url"],
            "http://wem-sg.local/",
        )
        self.assertTrue(ip_entity.device_info["configuration_url"].endswith("/"))
        self.assertNotIn("admin", ip_entity.device_info["configuration_url"])
        self.assertNotIn("secret", ip_entity.device_info["configuration_url"])

    def test_network_entities_enabled_and_ip_mode_mapping(self) -> None:
        """Network diagnostics should be enabled and use confirmed IP mode labels."""
        mode_def = next(
            item for item in sensors.NETWORK_SENSORS if item.key == "network_ip_mode"
        )
        self.assertFalse(any(item.poll for item in sensors.NETWORK_SENSORS))
        for sensor_def in sensors.NETWORK_SENSORS:
            self.assertTrue(sensor_def.entity_registry_enabled_default)
        auto_entity = sensor.WeishauptSensorEntity(
            coordinator=SimpleNamespace(
                data={"network_ip_mode": {"value_int": 3, "value_hex": "03"}}
            ),
            sensor_def=mode_def,
            entry=SimpleNamespace(entry_id="entry-123"),
        )
        manual_entity = sensor.WeishauptSensorEntity(
            coordinator=SimpleNamespace(
                data={"network_ip_mode": {"value_int": 1, "value_hex": "01"}}
            ),
            sensor_def=mode_def,
            entry=SimpleNamespace(entry_id="entry-123"),
        )

        self.assertEqual(auto_entity.native_value, "Automatisch (DHCP)")
        self.assertEqual(manual_entity.native_value, "Manuell")

    def test_system_operating_mode_current_mirrors_existing_data(self) -> None:
        """System operating-mode display should mirror the existing writable register."""
        entity = sensor.WeishauptSensorEntity(
            coordinator=SimpleNamespace(
                data={"sg_systembetriebsart": {"value_int": 2, "value_hex": "02"}}
            ),
            sensor_def=sensor_by_key("sg_systembetriebsart_aktuell"),
            entry=SimpleNamespace(entry_id="entry-123"),
        )

        self.assertTrue(entity.available)
        self.assertEqual(entity.native_value, "Sommer")

    def test_experimental_zero_is_valid_and_sentinel_is_unavailable(self) -> None:
        """Raw zero should remain valid while sentinel values are unavailable."""
        zero_register = next(
            item
            for item in sensors.EXPERIMENTAL_WTC_REGISTERS
            if item.key == "wtc_experimental_09_01_2619_02_01"
        )
        coordinator = SimpleNamespace(
            data={zero_register.key: {"value_int": 0, "value_hex": "00"}},
        )
        entity = sensor.WeishauptExperimentalWtcSensorEntity(
            coordinator=coordinator,
            register=zero_register,
            entry=SimpleNamespace(entry_id="entry-123"),
        )
        self.assertTrue(entity.available)
        self.assertEqual(entity.native_value, 0)

        sentinel_register = next(
            item
            for item in sensors.EXPERIMENTAL_WTC_REGISTERS
            if item.key == "wtc_experimental_09_01_2612_02_02"
        )
        coordinator.data = {
            sentinel_register.key: {"value_int": 0x8000, "value_hex": "8000"}
        }
        sentinel_entity = sensor.WeishauptExperimentalWtcSensorEntity(
            coordinator=coordinator,
            register=sentinel_register,
            entry=SimpleNamespace(entry_id="entry-123"),
        )
        self.assertFalse(sentinel_entity.available)
        self.assertIsNone(sentinel_entity.native_value)

    async def test_async_setup_entry_adds_no_experimental_entities_when_disabled(self) -> None:
        """An empty experimental register list should not add entities or device."""
        registry = DeviceRegistry()
        sensor.dr.async_get = lambda hass: registry
        added: list = []
        coordinator = SimpleNamespace(
            sensor_definitions=[],
            experimental_wtc_registers=[],
            extended_experimental_wtc_registers=[],
        )
        hass = SimpleNamespace(data={"weishaupt_wtc_lan": {"entry-123": coordinator}})

        await sensor.async_setup_entry(
            hass,
            SimpleNamespace(entry_id="entry-123"),
            lambda entities: added.extend(entities),
        )

        self.assertEqual(added, [])
        self.assertEqual(len(registry.created), 1)

    async def test_sensor_setup_skips_writable_setpoints_but_keeps_actual_states(self) -> None:
        """Read-only duplicate setpoint sensors should not be created for HK circuits."""
        registry = DeviceRegistry()
        sensor.dr.async_get = lambda hass: registry
        added: list = []
        coordinator = SimpleNamespace(
            sensor_definitions=[
                sensor_by_key("sg_betriebsart_hk1_vorgabe"),
                sensor_by_key("sg_betriebsart_hk1_aktuell"),
                next(item for item in sensors.HK_SENSORS if item.key == "hk_betriebsart_vorgabe"),
                next(item for item in sensors.HK_SENSORS if item.key == "hk_betriebsart_aktuell"),
            ],
            experimental_wtc_registers=[],
            extended_experimental_wtc_registers=[],
        )
        hass = SimpleNamespace(data={"weishaupt_wtc_lan": {"entry-123": coordinator}})

        await sensor.async_setup_entry(
            hass,
            SimpleNamespace(entry_id="entry-123"),
            lambda entities: added.extend(entities),
        )

        self.assertEqual(
            {entity._attr_unique_id for entity in added},
            {
                "entry-123_sg_betriebsart_hk1_aktuell",
                "entry-123_hk_betriebsart_aktuell",
            },
        )

    async def test_select_setup_keeps_writable_hk1_hk2_hk3_setpoints(self) -> None:
        """Writable operating-mode selects should remain for every detected circuit."""
        hk2 = next(item for item in sensors.HK_SENSORS if item.key == "hk_betriebsart_vorgabe")
        hk3 = heating_circuits.build_hk_sensor_definitions(3, 0x02)[0]
        coordinator = SimpleNamespace(
            sensor_definitions=[
                sensor_by_key("sg_betriebsart_hk1_vorgabe"),
                hk2,
                hk3,
                sensor_by_key("sg_systembetriebsart"),
            ],
            data={
                "sg_betriebsart_hk1_vorgabe": {"value_int": 5, "value_hex": "05"},
                "hk_betriebsart_vorgabe": {"value_int": 2, "value_hex": "02"},
                "hk3_betriebsart_vorgabe": {"value_int": 2, "value_hex": "02"},
                "sg_systembetriebsart": {"value_int": 2, "value_hex": "02"},
            },
        )
        added: list = []

        await select_platform.async_setup_entry(
            SimpleNamespace(data={"weishaupt_wtc_lan": {"entry-123": coordinator}}),
            SimpleNamespace(entry_id="entry-123"),
            lambda entities: added.extend(entities),
        )

        self.assertEqual(
            {entity._sensor_def.key for entity in added},
            {
                "sg_betriebsart_hk1_vorgabe",
                "hk_betriebsart_vorgabe",
                "hk3_betriebsart_vorgabe",
                "sg_systembetriebsart",
            },
        )
        hk2_select = next(
            entity for entity in added if entity._sensor_def.key == "hk_betriebsart_vorgabe"
        )
        self.assertEqual(hk2_select.current_option, "Zeitprogramm 1")


if __name__ == "__main__":
    unittest.main()
