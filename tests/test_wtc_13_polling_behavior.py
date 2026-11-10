"""Behavior tests of extracted WTC slow-poll method without HA hardware."""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
from typing import Any
import unittest

ROOT = Path(__file__).resolve().parents[1]
COORD = ROOT / "custom_components/weishaupt_wtc_lan/coordinator.py"


def extracted_method_class(clock):
    module = ast.parse(COORD.read_text(encoding="utf-8"))
    owner = next(n for n in module.body if isinstance(n, ast.ClassDef)
                 and n.name == "WeishauptDataUpdateCoordinator")
    method = next(n for n in owner.body if isinstance(n, ast.AsyncFunctionDef)
                  and n.name == "_async_poll_one_wtc_research_register")
    # Execute only the async polling method with controlled test dependencies.
    testing_class = ast.ClassDef(name="IsolatedCoordinator", bases=[], keywords=[],
                                 body=[copy.deepcopy(method)], decorator_list=[])
    isolated = ast.fix_missing_locations(ast.Module(body=[testing_class], type_ignores=[]))
    ns = {
        "Any": Any,
        "time": SimpleNamespace(monotonic=lambda: clock[0]),
        "WTC_RESEARCH_SLOW_POLL_GAP_SECONDS": 180.0,
        "WTC_RESEARCH_SLOW_POLL_KEYS": frozenset({"one", "two"}),
        "_LOGGER": SimpleNamespace(info=lambda *a: None,
                                   warning=lambda *a: None,
                                   exception=lambda *a: None),
    }
    exec(compile(isolated, str(COORD), "exec"), ns)
    return ns["IsolatedCoordinator"]


class FakeClient:
    def __init__(self):
        self.calls = []
        self.last_read_failed_batches = 0
        self.fail = False

    async def read_parameters(self, params):
        self.calls.append(params)
        self.last_read_failed_batches = int(self.fail)
        return {} if self.fail else {params[0]["key"]: {"value_int": 50}}


def make_defs():
    return [SimpleNamespace(key=k, poll=False, mi=7, mx=0,
                            ox=0x250A + i, os=0, vs=1, request_vs=None)
            for i, k in enumerate(("one", "two"))]


class SlowPollingBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def test_disabled_by_default_does_not_send_requests(self):
        clock = [0.0]
        coordinator = extracted_method_class(clock)()
        coordinator.sensor_definitions = make_defs()
        coordinator.client = FakeClient()
        coordinator.enable_wtc_research_polling = False
        self.assertEqual(await coordinator._async_poll_one_wtc_research_register(), {})
        self.assertEqual(coordinator.client.calls, [])

    async def test_interval_and_round_robin(self):
        clock = [0.0]
        cls = extracted_method_class(clock)
        coordinator = cls()
        coordinator.sensor_definitions = make_defs()
        coordinator.client = FakeClient()
        coordinator.enable_wtc_research_polling = True
        first = await coordinator._async_poll_one_wtc_research_register()
        self.assertEqual(list(first), ["one"])
        clock[0] = 179.0
        self.assertEqual(await coordinator._async_poll_one_wtc_research_register(), {})
        clock[0] = 180.0
        second = await coordinator._async_poll_one_wtc_research_register()
        self.assertEqual(list(second), ["two"])
        self.assertEqual(len(coordinator.client.calls), 2)
        self.assertEqual([call[0]["key"] for call in coordinator.client.calls], ["one", "two"])

    async def test_failure_pauses_until_restart(self):
        clock = [0.0]
        cls = extracted_method_class(clock)
        coordinator = cls()
        coordinator.sensor_definitions = make_defs()
        coordinator.client = FakeClient()
        coordinator.enable_wtc_research_polling = True
        coordinator.client.fail = True
        self.assertEqual(await coordinator._async_poll_one_wtc_research_register(), {})
        self.assertTrue(coordinator._wtc_research_poll_paused)
        coordinator.client.fail = False
        clock[0] = 360.0
        self.assertEqual(await coordinator._async_poll_one_wtc_research_register(), {})
        self.assertEqual(len(coordinator.client.calls), 1)


if __name__ == "__main__":
    unittest.main()
