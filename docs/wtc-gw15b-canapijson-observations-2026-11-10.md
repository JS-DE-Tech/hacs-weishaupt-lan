# WTC-GW 15-B: CanApiJson read-only observations (2026-11-10)

These observations were reported by an operator with a WTC-GW 15-B and a local
WEM CanApiJson interface. This is *hardware evidence* of specific responses,
not a blanket verification of semantic labels, scaling, stability, or all
Weishaupt equipment. Timestamps and operating state differ between readings.

## Individual one-shot GETs (confirmed replies)

| Candidate | CanApiJson MI/MX/OX/OS | GET VS | Reply VS | Reply raw | Provisional reading |
|---|---|---:|---:|---|---|
| Burner output | `07/00/2534/00` | 2 | 2 | `0x06A0` = 1696 | 16.96 % |
| Blower RPM | `07/00/2540/00` | 2 | 2 | `0x03F8` = 1016 | 1016 rpm |
| Internal pump electric power | `09/01/261B/02` | 2 | **1** | `0x0C` = 12 | 12 W |

The reply-size mismatch for pump power requires `request_vs=2` with `vs=1`.
When registered as regular Home Assistant sensors, blower speed and pump power
were later seen live as approximately 930--937 rpm and 12 W, respectively.
Burner output was `unavailable` in the regular HA sensor despite a successful
one-shot read; this issue is **unresolved** and must not be claimed fixed.

## Home Assistant experimental diagnostic snapshot

These are the *raw integers* displayed by Home Assistant, not necessarily
simultaneous values. `unavailable` means no valid state in this sample.

| CanApiJson MI/MX/OX/OS | Reported raw | Possible meaning from CAN docs |
|---|---:|---|
| `07/00/250A/00` | 10 | Burner anti-cycling time (minutes) |
| `07/00/250D/02` | 60 | Heating differential, likely 6.0 K |
| `07/00/256B/02` | unavailable | Minimum heating pump % |
| `07/00/256C/02` | 80 | Maximum heating pump % |
| `07/00/257E/00` | 0 | Blower control signal |
| `07/00/2523/02` | 6800 | Maximum heating burner output, likely 68% |
| `07/00/2534/00` | 0 | Current burner output (may be 0 at that instant) |
| `07/00/2536/00` | 500 | Boiler flow temperature, likely 50.0 °C |
| `07/00/2540/00` | unavailable | Blower RPM |
| `07/00/2542/00` | 0 | Burner output target |
| `09/01/263A/02` | unavailable | Existing curated experimental candidate |
| `09/01/2610/02` | 83 | Existing curated candidate; meaning unverified |
| `09/01/2611/02` | unavailable | Existing curated candidate; meaning unverified |
| `09/01/2612/02` | 473 | Existing curated candidate; meaning unverified |
| `09/01/2615/02` | unavailable | Existing curated candidate; suspected VPT flow temp |
| `09/01/2619/02` | 50 | Internal pump output target, likely 50% |
| `09/01/2629/02` | 2200 | Maximum VPT flow, likely 2200 l/h |
| `09/01/2679/00` | 450 | Existing curated candidate; meaning unverified |
| `09/01/2903/00` | 124 | Existing curated candidate; meaning unverified |

Nine of the eleven new extended-register addresses shown above yielded numeric
results in this snapshot; response success does not establish semantic meaning.

## Scope and precautions

- The PR adds 13 named, read-only diagnostic entities; it does **not** change
  WEM settings or send CanApiJson SET commands.
- Three one-shot-responsive candidates use existing ordinary HA polling.
- Ten further candidate entities are not part of normal batches. A separate
  single-register scheduler reads at most one every 180 seconds *total*;
  a failure of a read batch or processing pauses that loop until restart.
- Both legacy experimental catalog options should remain **off** to avoid
  duplicate register queries. The older curated experimental diagnostics already
  exist upstream and are not duplicated here.
- Candidate names and units are provisional where not validated against WEM
  display/portal. Do not merge as broadly hardware-verified.
- The separate 180-second scheduling strategy is *not* a proven cure for WEM
  instability, and still increases request traffic; observe it on hardware.

Sources for CAN semantics:
- https://github.com/geronet1/wem-python/blob/main/wem_codes.py
- https://github.com/jvejmelka/weishaupt-wem-can-esphome/blob/main/PROTOKOLL.md

The CAN object identifiers and JSON register addressing are related but should
not be conflated; this document distinguishes observed CanApiJson replies from
hypothesized interpretations.
