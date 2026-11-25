"""Test local device clock handling."""

import importlib.util
import unittest

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "weishaupt_wtc_lan"
    / "clock.py"
)

spec = importlib.util.spec_from_file_location(
    "weishaupt_clock", PATH
)
clock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clock)

TZ = ZoneInfo("Europe/Berlin")


def values(month=11, day=26, hour=12, minute=0):
    return {
        "sg_datum_jahr": 26,
        "sg_datum_monat": month,
        "sg_datum_tag": day,
        "sg_uhrzeit_stunden": hour,
        "sg_uhrzeit_minuten": minute,
    }


class ClockTests(unittest.TestCase):

    def test_winter_timezone(self):
        self.assertEqual(
            clock.device_timestamp(values(), TZ),
            "2026-11-26T12:00:00+01:00",
        )

    def test_summer_timezone(self):
        self.assertEqual(
            clock.device_timestamp(values(month=6), TZ),
            "2026-06-26T12:00:00+02:00",
        )

    def test_zero_drift(self):
        now = datetime(
            2026, 11, 26, 11, 0, 45, tzinfo=timezone.utc
        )
        self.assertEqual(
            clock.clock_drift_seconds(values(), now, TZ), 0
        )

    def test_clock_ahead(self):
        now = datetime(
            2026, 11, 26, 11, 0, tzinfo=timezone.utc
        )
        self.assertEqual(
            clock.clock_drift_seconds(
                values(minute=5), now, TZ
            ), 300
        )

    def test_clock_behind(self):
        now = datetime(
            2026, 11, 26, 11, 5, tzinfo=timezone.utc
        )
        self.assertEqual(
            clock.clock_drift_seconds(values(), now, TZ), -300
        )

    def test_midnight(self):
        now = datetime(
            2026, 11, 25, 23, 0, tzinfo=timezone.utc
        )
        self.assertEqual(
            clock.clock_drift_seconds(
                values(day=25, hour=23, minute=59),
                now,
                TZ,
            ), -60
        )

    def test_missing_components(self):
        data = values()
        del data["sg_datum_tag"]
        self.assertIsNone(clock.device_timestamp(data, TZ))

    def test_invalid_date(self):
        self.assertIsNone(
            clock.device_timestamp(values(month=2, day=31), TZ)
        )

    def test_invalid_hour(self):
        self.assertIsNone(
            clock.device_timestamp(values(hour=24), TZ)
        )

    def test_valid_zero_hour_and_minute(self):
        self.assertEqual(
            clock.device_timestamp(values(hour=0), TZ),
            "2026-11-26T00:00:00+01:00",
        )

    def test_spring_dst_gap(self):
        self.assertIsNone(
            clock.device_timestamp(
                values(month=3, day=29, hour=2, minute=30),
                TZ,
            )
        )

    def test_autumn_dst_ambiguity(self):
        self.assertIsNone(
            clock.device_timestamp(
                values(month=10, day=25, hour=2, minute=30),
                TZ,
            )
        )

    def test_fresh_results(self):
        data = {
            key: {"value_int": value}
            for key, value in values().items()
        }
        now = datetime(
            2026, 11, 26, 11, 0, tzinfo=timezone.utc
        )
        self.assertEqual(
            clock.drift_from_results(data, now, "Europe/Berlin"),
            0,
        )

        del data["sg_datum_tag"]

        self.assertIsNone(
            clock.drift_from_results(data, now, "Europe/Berlin")
        )


if __name__ == "__main__":
    unittest.main()
