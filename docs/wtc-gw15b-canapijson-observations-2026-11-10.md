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

- PR #14 retains 13 read-only candidate entities and stable unique IDs.
- The 13 are now ordinary WTC sensor entities without diagnostic category.
- All 13 use the existing regular Home Assistant coordinator polling; no
  research-only 180-second round robin or research opt-in toggle remains.
- The default update interval is 60 seconds; users with saved integration options
  should explicitly set 60 seconds.
- Older experimental catalog options remain off by default.
- This is NOT proof of reliable long-term batching on different firmware.
  Individual GET responses previously succeeded even when grouped GETs failed.
- Real-world cross-check: electrical pump power 11 W matched the display at
  11 W; minimum/maximum pump settings 30/80 matched 30%/80%; flow target 42.3°C
  matched. Fan speed and burner modulation comparisons were asynchronous.
- Burner target output and blower signal remain unconfirmed; pump mode raw 9
  matched a display reading of Konstantdruck Stufe 2 but is not yet generalized.
- Do not change heating settings to validate candidates; no SET command added.

Sources for CAN semantics:
- https://github.com/geronet1/wem-python/blob/main/wem_codes.py
- https://github.com/jvejmelka/weishaupt-wem-can-esphome/blob/main/PROTOKOLL.md

The CAN object identifiers and JSON register addressing are related but should
not be conflated; this document distinguishes observed CanApiJson replies from
hypothesized interpretations.

### WTC-GW 15-B on-device display cross-check — 2026-11-10

On the WTC-GW 15-B, two read-only CanApiJson candidates were compared with
the corresponding values displayed by the controller during burner operation.
The operator reported agreement with the controller display.

| WTC register | Candidate sensor | Timestamp (local) | Raw | Scale | Display-matched value |
|---|---|---|---:|---:|---:|
| `07/00/2542/00` | Burner target output | 21:13:02 | 1569 | 0.01 | 15.69 % |
| `07/00/2542/00` | Burner target output | 21:13:58 | 1569 | 0.01 | 15.69 % |
| `07/00/257E/00` | Blower control signal | 21:13:07 | 1042 | 0.01 | 10.42 % |
| `07/00/257E/00` | Blower control signal | 21:14:03 | 1041 | 0.01 | 10.41 % |

Earlier, the burner target register also returned a valid raw `0` during a
different operating state. Retain zero as a valid value. The two sensor keys
remain unchanged to preserve existing Home Assistant entity registry IDs.
These observations apply to the tested controller; wider firmware/model
compatibility and sustained regular batch-poll stability still need checking.

## Controller comparison update: 2026-11-10 (WTC-GW 15-B)

Two direct read-only CanApiJson GETs were repeated during burner operation;
the user compared the corresponding display values and reported agreement:

| Display item | Address | Read time (local) | Raw | Decoded at /100 |
|---|---|---|---:|---:|
| Burner output target | `07/00/2542/00` | 21:13:02 | 1569 | 15.69 % |
| Blower control signal | `07/00/257E/00` | 21:13:07 | 1042 | 10.42 % |
| Burner output target | `07/00/2542/00` | 21:13:58 | 1569 | 15.69 % |
| Blower control signal | `07/00/257E/00` | 21:14:03 | 1041 | 10.41 % |

Other operator-reported display comparisons: electric pump power **11 W** in
both HA and WTC; minimum and maximum pump limits **30 % / 80 %**; pump mode
raw **9** corresponded to **Konstantdruck Stufe 2** for this controller. The
full pump-mode enum is not known and other modes remain unmapped. Burner actual
output and blower speed were plausible but not strictly time-synchronized.

All 13 registers have returned numeric responses in standalone probes. This is
confirmation of readable addresses on this WTC-GW 15-B, **not** full proof of
physical meaning, scaling, stable batched polling or cross-device compatibility.
Display names no longer contain provisional suffixes, but unverified raw values
have **not** been given guessed units or scales. The internal sensor keys keep
`_kandidat` because changing them would change HA entity unique IDs.

Previously observed raw zero for burner target can be a legitimate operating
state. No WEM configuration was changed, no SET requests were sent.
