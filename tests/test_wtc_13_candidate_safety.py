"""Regression protection for regular, read-only WTC candidate polling."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SENSORS = (ROOT / "custom_components/weishaupt_wtc_lan/sensors.py").read_text(encoding="utf-8")
COORD = (ROOT / "custom_components/weishaupt_wtc_lan/coordinator.py").read_text(encoding="utf-8")
CONFIG = (ROOT / "custom_components/weishaupt_wtc_lan/config_flow.py").read_text(encoding="utf-8")
INIT = (ROOT / "custom_components/weishaupt_wtc_lan/__init__.py").read_text(encoding="utf-8")

class NormalWtcPollingSafetyTests(unittest.TestCase):
    def test_python_compiles(self):
        for source in (SENSORS, COORD, CONFIG, INIT):
            ast.parse(source)

    def test_obsolete_research_scheduler_is_gone(self):
        for source in (COORD, CONFIG, INIT):
            self.assertNotIn("enable_wtc_research_polling", source)
        self.assertNotIn("_async_poll_one_wtc_research_register", COORD)
        self.assertNotIn("WTC_RESEARCH_SLOW_POLL_GAP_SECONDS", COORD)

    def test_all_thirteen_are_regular_wtc_sensors(self):
        tree = ast.parse(SENSORS)
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "WeishauptSensorDefinition":
                opts = {k.arg: k.value for k in node.keywords}
                key = opts.get("key")
                if isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value.startswith("wtc_") and key.value.endswith("_kandidat"):
                    definitions.append(opts)
        self.assertEqual(len(definitions), 13)
        for d in definitions:
            self.assertNotIn("poll", d)
            self.assertNotIn("entity_category", d)
            self.assertEqual(ast.unparse(d["group"]), "WeishauptDeviceGroup.WTC")

    def test_default_interval_is_sixty_seconds(self):
        constants = (ROOT / "custom_components/weishaupt_wtc_lan/const.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_SCAN_INTERVAL = 60", constants)

if __name__ == "__main__":
    unittest.main()
