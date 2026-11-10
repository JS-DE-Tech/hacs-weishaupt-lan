# PR #14 — normal WTC sensor polling (60-second default)

## Summary

The 13 read-only WTC sensor entities are assigned directly to the existing
**WTC Brennwertgerät** device as ordinary sensor entities. Their existing sensor
keys / Home Assistant unique IDs are preserved. No entities are categorized as
`diagnostic`. The extra research-only round-robin polling path, 180-second
rate limit, and the research opt-in toggle have been removed.

All 13 are now read alongside ordinary sensor definitions through the existing
coordinator and CanApiJson batch reader. The default integration interval is
**60 seconds** (still user-configurable). Existing configured intervals are not
overwritten; users of this development branch should set 60 seconds explicitly.
The separate legacy experimental catalogs remain disabled by default.

## Important cautions

A 60-second interval was reported to restore stable operation on one
WTC-GW 15-B installation, but **long-term stability with all 13 registers in
normal batches has not yet been demonstrated**. More registers per cycle
increase traffic and previously some batch reads failed even when standalone
requests succeeded. Watch for failed batches or unavailable sensors.
Do not merge as universally stable solely based on local observations.

These sensor IDs still carry `_kandidat` to preserve entity-registry identity.
Display names are clean and ordinary WTC labels; no unsupported scale or enum
mapping is inferred. *Internal pump electrical power* had matching 11 W
HA/display readings (not time-synchronized). All calls remain read-only (GET).

## Hardware display comparisons — 2026-11-10

- Internal pump electrical power: Home Assistant **11 W**, WTC display **11 W**.
  The 50% pump command is *a different physical quantity*.
- Minimum/maximum pump limits: 30 / 80 in HA vs 30% / 80% on display.
- Flow temperature target: 42.3 °C in both readings.
- Burner actual output: 19.1% HA vs 21.9% display at different times (plausible,
  not a simultaneous validation).
- Blower speed: 1121 rpm HA vs 1048 rpm display at different times (plausible).
- Burner target output: raw 0 at a prior time vs 17.2% display (unresolved).
- Fan control signal: raw 1312 vs 11.2% display (mapping unresolved).
- Pump control mode: raw 9 vs Konstantdruck Stufe 2 (provisional enum candidate).
- Max VPT flow: raw 2200 from standalone test, sometimes unavailable in HA.

No write operations or changes to heating settings were performed.

## Reproducible read-only validation

The one-shot `scripts/wtc13_probe.py` still performs 13 individual GET requests
with at least three seconds pause; do not run it continuously alongside HA.
Read dynamic values simultaneously on the WTC display and in HA. Preserve raw
VG responses and the exact timestamps. Only confirm an enum or scale after
repeatability across more than one observed condition. Follow the companion
observations document for register addresses and caveats.

## Display naming and validation status (2026-11-10)

The 13 extra WTC sensors have ordinary, suffix-free display names and use
the existing WTC device. The entity keys still carry `_kandidat` by design:
changing keys would create new HA entities and break existing unique IDs.
Register responses were confirmed on one WTC-GW 15-B; semantics of some
raw readings (e.g. heating differential, boiler flow value and maximal VPT
flow) have not been cross-checked. Unit/scale were only set where evidence
supports them. See the 2026-11-10 observation log for the two repeated
percentage-register comparisons and pump observations.
