"""Safety regression checks for opt-in candidate register polling."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENSORS = (ROOT / "custom_components/weishaupt_wtc_lan/sensors.py").read_text(encoding="utf-8")
COORD = (ROOT / "custom_components/weishaupt_wtc_lan/coordinator.py").read_text(encoding="utf-8")

class CandidatePollingStructureTests(unittest.TestCase):
    def test_python_compiles(self):
        ast.parse(SENSORS)
        ast.parse(COORD)

    def test_ten_candidate_keys_in_slow_poll_catalog(self):
        tree = ast.parse(COORD)
        matches = [node for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "WTC_RESEARCH_SLOW_POLL_KEYS"
                           for t in node.targets)]
        self.assertEqual(len(matches), 1)
        vals = ast.literal_eval(matches[0].value.args[0])
        self.assertEqual(len(vals), 10)
        self.assertEqual(len(vals), len(set(vals)))

    def test_slow_poll_has_one_separate_read_and_rate_limit(self):
        self.assertIn("WTC_RESEARCH_SLOW_POLL_GAP_SECONDS = 180.0", COORD)
        self.assertIn("read_parameters([param])", COORD)
        self.assertIn("_wtc_research_poll_paused = True", COORD)
        self.assertIn("results.update(await self._async_poll_one_wtc_research_register())", COORD)

if __name__ == "__main__":
    unittest.main()
