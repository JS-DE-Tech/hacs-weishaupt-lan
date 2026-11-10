"""Standalone regression tests for scripts/wtc13_probe.py (no HA or WEM required)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PROBE = Path(__file__).resolve().parents[1] / "scripts" / "wtc13_probe.py"
spec = importlib.util.spec_from_file_location("wtc13_probe_tested", PROBE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class CandidateProbeTests(unittest.TestCase):
    def test_thirteen_unique_candidates(self):
        self.assertEqual(len(mod.CANDIDATES), 13)
        self.assertEqual(len({c.key for c in mod.CANDIDATES}), 13)
        self.assertEqual(len({(c.mi, c.mx, c.ox, c.os) for c in mod.CANDIDATES}), 13)

    def test_all_requests_are_get_frames(self):
        for c in mod.CANDIDATES:
            with self.subTest(key=c.key):
                vg = mod.read_payload(c)["CAPI"]["N01"]["VG"]
                self.assertEqual(vg[:2], "01")  # Only CMD_GET allowed
                self.assertEqual(int(vg[12:16], 16), c.request_vs)
                self.assertEqual(len(vg), 16 + c.request_vs * 2)

    def test_pump_request_vs_two_reply_vs_one(self):
        c = next(c for c in mod.CANDIDATES if c.ox == 0x261B)
        self.assertEqual((c.request_vs, c.response_vs), (2, 1))
        reply = f"02{c.mi:02x}{c.mx:02x}{c.ox:04x}{c.os:02x}00010c"
        self.assertEqual(mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)["raw_unsigned"], 12)

    def test_confirmed_reply_is_parsed_as_raw(self):
        c = mod.CANDIDATES[0]
        reply = f"02{c.mi:02x}{c.mx:02x}{c.ox:04x}{c.os:02x}000206a0"
        parsed = mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)
        self.assertEqual(parsed["status"], "response")
        self.assertEqual(parsed["raw_unsigned"], 1696)

    def test_cmd_error_never_decoded_as_numeric(self):
        c = mod.CANDIDATES[0]
        reply = f"05{c.mi:02x}{c.mx:02x}{c.ox:04x}{c.os:02x}00020000"
        parsed = mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)
        self.assertEqual(parsed["status"], "unsupported_or_error")
        self.assertNotIn("raw_unsigned", parsed)

    def test_unavailable_sentinel_is_not_reported_as_measurement(self):
        c = mod.CANDIDATES[0]
        reply = f"02{c.mi:02x}{c.mx:02x}{c.ox:04x}{c.os:02x}0002ffff"
        result = mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)
        self.assertEqual(result["status"], "sentinel_unavailable")
        self.assertNotIn("raw_unsigned", result)

    def test_mismatched_address_rejected(self):
        c = mod.CANDIDATES[0]
        reply = f"02{c.mi:02x}{c.mx:02x}9999{c.os:02x}00020000"
        self.assertEqual(mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)["status"], "wrong_address")

    def test_mismatched_response_vs_rejected(self):
        c = mod.CANDIDATES[0]
        reply = f"02{c.mi:02x}{c.mx:02x}{c.ox:04x}{c.os:02x}000100"
        self.assertEqual(mod.parse_reply({"CAPI": {"N01": {"VG": reply}}}, c)["status"], "wrong_response_size")

    def test_dry_run_does_not_access_network(self):
        with patch.object(mod, "urlopen", side_effect=AssertionError("network call")):
            rows = mod.probe("", "", "", pause=3, timeout=15, dry_run=True)
        self.assertEqual(len(rows), 13)
        self.assertTrue(all(row["status"] == "dry_run" for row in rows))


if __name__ == "__main__":
    unittest.main()
