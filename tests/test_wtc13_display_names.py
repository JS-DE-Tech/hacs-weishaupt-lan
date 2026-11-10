"""Display naming + conservative value metadata for the 13 WTC read-only sensors.

These tests purposely do not claim that all 13 physical meanings are validated.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "custom_components" / "weishaupt_wtc_lan" / "sensors.py"
NAMES = {'wtc_brenner_istleistung_kandidat': 'Brenner-Istleistung', 'wtc_geblaesedrehzahl_kandidat': 'Gebläsedrehzahl', 'wtc_pumpe_intern_elektrische_leistung_kandidat': 'Interne Pumpe elektrische Leistung', 'wtc_kessel_vorlauf_ist_kandidat': 'Kessel-Vorlauftemperatur', 'wtc_brenner_sollleistung_kandidat': 'Brenner-Sollleistung', 'wtc_geblaese_ansteuerung_kandidat': 'Gebläse-Ansteuersignal', 'wtc_brennertaktsperre_kandidat': 'Brennertaktsperre', 'wtc_schaltdifferenz_heizbetrieb_kandidat': 'Schaltdifferenz Heizbetrieb', 'wtc_brennerleistung_max_heizbetrieb_kandidat': 'Maximale Brennerleistung Heizbetrieb', 'wtc_pumpenleistung_min_heizbetrieb_kandidat': 'Minimale Pumpenleistung Heizbetrieb', 'wtc_pumpenleistung_max_heizbetrieb_kandidat': 'Maximale Pumpenleistung Heizbetrieb', 'wtc_pumpenregelungsart_kandidat': 'Pumpenregelungsart', 'wtc_vpt_max_volumenstrom_kandidat': 'Maximaler VPT-Volumenstrom'}
SCALED = {"wtc_brenner_istleistung_kandidat", "wtc_brenner_sollleistung_kandidat", "wtc_geblaese_ansteuerung_kandidat"}
PERCENT = SCALED | {"wtc_pumpenleistung_min_heizbetrieb_kandidat", "wtc_pumpenleistung_max_heizbetrieb_kandidat"}


def definitions():
    tree = ast.parse(FILE.read_text(encoding="utf-8"))
    result = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "WeishauptSensorDefinition"):
            continue
        args = {arg.arg: arg.value for arg in node.keywords}
        key = args.get("key")
        if isinstance(key, ast.Constant) and key.value in NAMES:
            if key.value in result:
                raise AssertionError(f"duplicate definition: {key.value}")
            result[key.value] = args
    return result


def literal(args, key, default=None):
    return ast.literal_eval(args[key]) if key in args else default


class WtcDisplayPresentationTests(unittest.TestCase):
    def test_all_thirteen_ids_and_clean_names(self):
        ds = definitions()
        self.assertEqual(set(ds), set(NAMES))
        for key, expected in NAMES.items():
            with self.subTest(key=key):
                self.assertEqual(literal(ds[key], "name"), expected)
                self.assertNotIn("kandidat", expected.lower())
                self.assertNotIn("unbestätigt", expected.lower())
                self.assertTrue(key.endswith("_kandidat"))  # stable HA unique_id

    def test_regular_wtc_not_diagnostics(self):
        for key, args in definitions().items():
            with self.subTest(key=key):
                self.assertEqual(ast.unparse(args["group"]), "WeishauptDeviceGroup.WTC")
                self.assertNotIn("entity_category", args)
                self.assertTrue(literal(args, "poll", True))
                self.assertTrue(literal(args, "entity_registry_enabled_default", True))
                self.assertNotIn("candidate", literal(args, "modbus_reg", "").lower())

    def test_display_matched_percent_scales(self):
        for key in PERCENT:
            with self.subTest(key=key):
                args = definitions()[key]
                self.assertEqual(literal(args, "unit"), "%")
                self.assertEqual(literal(args, "scale", 1.0), 0.01 if key in SCALED else 1.0)

    def test_pump_electric_power_and_response_size(self):
        args = definitions()["wtc_pumpe_intern_elektrische_leistung_kandidat"]
        self.assertEqual(literal(args, "unit"), "W")
        self.assertEqual(literal(args, "vs"), 1)
        self.assertEqual(literal(args, "request_vs"), 2)

    def test_pump_mode_only_observed_enum_is_mapped(self):
        args = definitions()["wtc_pumpenregelungsart_kandidat"]
        self.assertEqual(literal(args, "value_map"), {9: "Konstantdruck Stufe 2"})

    def test_unverified_raw_values_do_not_get_invented_units(self):
        raw_keys = {
            "wtc_kessel_vorlauf_ist_kandidat",
            "wtc_brennertaktsperre_kandidat",
            "wtc_schaltdifferenz_heizbetrieb_kandidat",
            "wtc_brennerleistung_max_heizbetrieb_kandidat",
            "wtc_vpt_max_volumenstrom_kandidat",
        }
        for key in raw_keys:
            with self.subTest(key=key):
                self.assertIsNone(literal(definitions()[key], "unit"))
                self.assertEqual(literal(definitions()[key], "scale", 1.0), 1.0)

if __name__ == "__main__":
    unittest.main()
