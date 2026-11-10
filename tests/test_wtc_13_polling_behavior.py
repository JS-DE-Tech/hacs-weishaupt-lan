"""Check 13 WTC candidate entities use the ordinary coordinator read path."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SENSORS = (ROOT / "custom_components/weishaupt_wtc_lan/sensors.py").read_text(encoding="utf-8")
COORD = (ROOT / "custom_components/weishaupt_wtc_lan/coordinator.py").read_text(encoding="utf-8")

class NormalPollingBehaviorTests(unittest.TestCase):
    def test_no_separate_research_loop(self):
        self.assertNotIn("_async_poll_one_wtc_research_register", COORD)
        self.assertNotIn("results.update(await self._async_poll_one_wtc_research_register())", COORD)

    def test_ordinary_coordinator_builds_requests_from_polled_definitions(self):
        self.assertIn("for sensor_def in self.polled_sensor_definitions", COORD)
        self.assertIn("results = await self.client.read_parameters(params)", COORD)
        tree = ast.parse(SENSORS)
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "WeishauptSensorDefinition":
                continue
            d = {kw.arg: kw.value for kw in node.keywords}
            key = d.get("key")
            if isinstance(key, ast.Constant) and isinstance(key.value, str) and key.value.startswith("wtc_") and key.value.endswith("_kandidat"):
                self.assertNotIn("poll", d)
                self.assertNotIn("entity_category", d)
                found.append(key.value)
        self.assertEqual(len(set(found)), 13)

    def test_request_size_override_still_supported(self):
        self.assertIn('"request_vs": sensor_def.request_vs or sensor_def.vs', COORD)

if __name__ == "__main__":
    unittest.main()
