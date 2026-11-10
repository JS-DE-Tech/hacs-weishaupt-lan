"""Static safety checks for WTC diagnostic candidates, independent of HA runtime."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SENSORS = ROOT / "custom_components" / "weishaupt_wtc_lan" / "sensors.py"
COORD = ROOT / "custom_components" / "weishaupt_wtc_lan" / "coordinator.py"

EXPECTED = {
    "wtc_brenner_istleistung_kandidat": (0x07, 0x00, 0x2534, 0x00, 2, None, True),
    "wtc_geblaesedrehzahl_kandidat": (0x07, 0x00, 0x2540, 0x00, 2, None, True),
    "wtc_pumpe_intern_elektrische_leistung_kandidat": (0x09, 0x01, 0x261B, 0x02, 1, 2, True),
    "wtc_kessel_vorlauf_ist_kandidat": (0x07, 0x00, 0x2536, 0x00, 2, None, True),
    "wtc_brenner_sollleistung_kandidat": (0x07, 0x00, 0x2542, 0x00, 2, None, True),
    "wtc_geblaese_ansteuerung_kandidat": (0x07, 0x00, 0x257E, 0x00, 2, None, True),
    "wtc_brennertaktsperre_kandidat": (0x07, 0x00, 0x250A, 0x00, 1, None, True),
    "wtc_schaltdifferenz_heizbetrieb_kandidat": (0x07, 0x00, 0x250D, 0x02, 2, None, True),
    "wtc_brennerleistung_max_heizbetrieb_kandidat": (0x07, 0x00, 0x2523, 0x02, 2, None, True),
    "wtc_pumpenleistung_min_heizbetrieb_kandidat": (0x07, 0x00, 0x256B, 0x02, 1, None, True),
    "wtc_pumpenleistung_max_heizbetrieb_kandidat": (0x07, 0x00, 0x256C, 0x02, 1, None, True),
    "wtc_pumpenregelungsart_kandidat": (0x09, 0x01, 0x266A, 0x02, 1, None, True),
    "wtc_vpt_max_volumenstrom_kandidat": (0x09, 0x01, 0x2629, 0x02, 2, None, True),
}


def definitions():
    parsed = ast.parse(SENSORS.read_text(encoding="utf-8"))
    found = {}
    for node in ast.walk(parsed):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "WeishauptSensorDefinition":
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords}
        if "key" not in kwargs:
            continue
        try:
            key = ast.literal_eval(kwargs["key"])
        except (ValueError, TypeError):
            continue
        if key in EXPECTED:
            if key in found:
                raise AssertionError(f"Duplicate candidate definition: {key}")
            found[key] = kwargs
    return found


def arg(kwargs, field, default=None):
    return ast.literal_eval(kwargs[field]) if field in kwargs else default


class WtcCandidateSafetyTests(unittest.TestCase):
    def test_all_thirteen_keys_exist_once(self):
        self.assertEqual(set(definitions()), set(EXPECTED))

    def test_addresses_response_sizes_and_polling(self):
        for key, (mi, mx, ox, os, vs, request_vs, is_regular) in EXPECTED.items():
            with self.subTest(key=key):
                d = definitions()[key]
                self.assertEqual([arg(d, k) for k in ("mi", "mx", "ox", "os", "vs")],
                                 [mi, mx, ox, os, vs])
                self.assertEqual(arg(d, "request_vs"), request_vs)
                self.assertEqual(arg(d, "poll", True), is_regular)
                self.assertIsNone(arg(d, "entity_category"))

    def test_all_thirteen_candidates_use_normal_polling(self):
        self.assertEqual(sum(arg(d, "poll", True) for d in definitions().values()), 13)

    def test_special_pump_value_size_is_preserved(self):
        d = definitions()["wtc_pumpe_intern_elektrische_leistung_kandidat"]
        self.assertEqual(arg(d, "vs"), 1)
        self.assertEqual(arg(d, "request_vs"), 2)

    def test_no_special_polling_scheduler(self):
        self.assertNotIn("_async_poll_one_wtc_research_register", COORD.read_text(encoding="utf-8"))
        self.assertNotIn("WTC_RESEARCH_SLOW_POLL_GAP_SECONDS", COORD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
