"""Local device clock diagnostics without additional protocol reads."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

CLOCK_KEYS = (
    "sg_datum_jahr",
    "sg_datum_monat",
    "sg_datum_tag",
    "sg_uhrzeit_stunden",
    "sg_uhrzeit_minuten",
)

DRIFT_KEY = "sg_device_clock_drift"


def device_wall_time(values):
    """Decode complete local device date and time components."""
    try:
        year, month, day, hour, minute = (
            values[key] for key in CLOCK_KEYS
        )

        if not all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (year, month, day, hour, minute)
        ):
            return None

        if not 0 <= year <= 99:
            return None

        return datetime(
            2000 + year, month, day, hour, minute
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def device_clock_candidates(values, tz):
    """Return valid timezone-aware interpretations of local time."""
    wall = device_wall_time(values)
    if wall is None:
        return []

    candidates = {}

    for fold in (0, 1):
        candidate = wall.replace(tzinfo=tz, fold=fold)
        utc = candidate.astimezone(timezone.utc)

        if utc.astimezone(tz).replace(tzinfo=None) == wall:
            candidates[utc] = candidate

    return list(candidates.values())


def device_timestamp(values, tz):
    """Return an unambiguous timezone-aware ISO timestamp."""
    candidates = device_clock_candidates(values, tz)

    if len(candidates) != 1:
        return None

    return candidates[0].isoformat()


def clock_drift_seconds(values, now, tz):
    """Calculate signed minute-resolution clock drift.

    Positive means the device clock is ahead.
    Negative means the device clock is behind.
    Ambiguous or invalid local times are unavailable.
    """
    if now.tzinfo is None:
        return None

    candidates = device_clock_candidates(values, tz)
    if len(candidates) != 1:
        return None

    reference = now.astimezone(tz).replace(
        second=0, microsecond=0
    )

    return int(
        (
            candidates[0].astimezone(timezone.utc)
            - reference.astimezone(timezone.utc)
        ).total_seconds()
    )


def drift_from_results(results, now, timezone_name):
    """Calculate drift only from complete fresh read results."""
    try:
        values = {
            key: results[key]["value_int"]
            for key in CLOCK_KEYS
        }
        tz = ZoneInfo(timezone_name)
    except (KeyError, TypeError, ValueError, ZoneInfoNotFoundError):
        return None

    return clock_drift_seconds(values, now, tz)


def drift_from_poll_window(results, started, finished, timezone_name):
    """Estimate drift from a bounded polling observation window."""
    try:
        tz = ZoneInfo(timezone_name)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        return None

    elapsed = (finished - started).total_seconds()

    if not 0 <= elapsed <= 60:
        return None

    local_start = started.astimezone(tz)
    local_finish = finished.astimezone(tz)

    if local_start.date() != local_finish.date():
        return None

    if local_start.utcoffset() != local_finish.utcoffset():
        return None

    midpoint = started + (finished - started) / 2

    return drift_from_results(
        results, midpoint, timezone_name
    )
