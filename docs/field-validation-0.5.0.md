# Field validation for 0.5.0

## What this release establishes

The WTC-GW 25-B installation was inspected through read-only CanApiJson GET requests and device-display photographs. No operating modes, actuators or combustion settings were changed. A valid register response establishes readability; it does not by itself prove a semantic interpretation.

### Confirmed HK2 mixer readings

| Sensor key | Address MI/MX/OX/OS | VS | Scale |
|---|---|---|---|
| `hk_mischerstellung_soll` | `02/01/2536/02` | 1 | 1 % |
| `hk_mischerstellung_ist` | `02/01/254F/02` | 1 | 1 % |

A display photo showed target 53%, actual 52% and a 36.6 C flow temperature. GET responses five seconds before and six seconds after that photo returned 53% and 52%; the flow temperature was 36.6/36.4 C. A separate earlier comparison showed 57/56%. These are controller-reported positions, not a claim about an independent mechanical position sensor. The full 0-100% range has not been physically exercised.

Only detected HK2 receives these normal read-only sensors. A mixer is not inferred for HK1 or HK3. No new writable mixer control is introduced.

### Heating-circuit pump readings and remaining candidates

Normal read-only `hk_pumpe_heizkreis` and `hk3_pumpe_heizkreis` sensors use `02/01/2546/02` and `02/02/2546/02` (VS=1), directly on the existing HK2/HK3 devices without an EXP label. The optional diagnostic HK1 pump remains at `02/00/2546/02`. Raw 1 agrees with displayed ON for HK2/HK3. Raw 0 uses the existing pump mapping but has not yet been observed in a matching physical OFF comparison. The controller state is not proof of physical rotation or an electrical supply measurement.

HK1/HK3 mixer candidates remain optional and unconfirmed. The EXP display-name prefix and diagnostic categories distinguish these from normal sensors. HK2 mixer and HK2/HK3 pump registers are not polled twice when candidates are enabled.

### Extended WTC combustion candidates

All entries below are optional, read-only, named with an EXP prefix on the experimental diagnostic device. Both experimental WTC and extended experimental WTC options must be enabled. Setup probes only include supported registers; zero is a valid response.

| Key suffix (`wtc_candidate_`) | Address | VS | Candidate scale/unit | Observed raw -> interpreted |
|---|---|---|---|---|
| `geblaesedrehzahl` | `07/00/2540/00` | 2 | 1 rpm | 995 -> 995 rpm |
| `geblaese_ansteuersignal` | `07/00/257E/00` | 2 | 0.01 % | 1029 -> 10.29% |
| `gasventil_ansteuersignal` | `07/00/253F/00` | 2 | 0.01 % | 3169 -> 31.69% |
| `gas_luft_verhaeltnis` | `07/00/257D/00` | 2 | 0.01 % | 5872 -> 58.72% |
| `ionisation_soll` | `07/00/2579/00` | 1 | 1 point | 48 -> 48 |
| `ionisation_start` | `07/00/257A/00` | 1 | 1 point | 19 -> 19 |
| `ionisation_scot_ist` | `07/00/2539/00` | 1 | 1 point | 48 -> 48 |
| `ionisation_scot_basis` | `07/00/253A/00` | 1 | 1 point | 91 -> 91 |

Interpretations/scales are research candidates from [geronet1/wem-python, wem_codes.py](https://github.com/geronet1/wem-python/blob/main/wem_codes.py), cross-checked with archived CanApiJson response addresses and lengths. This is not copied executable code. Historical GETs also returned these objects; the latest targeted GETs established current readability. The SCOT base value matches an earlier display photo, but there is no simultaneous display capture for this entire group. Simultaneous comparison during normal burner operation remains required before promotion. These numbers must not drive real combustion controls.

The internal pump modulation candidate `09/01/2619/02 VS=1` returns 100, matching a time-separated 100% display. Its correct menu reference is **1.2.2.2**, not the burner-output entry 1.2.1.3.

### Not included / unresolved

- `07/00/253D/00` (gas-valve offset) and `07/00/257B/00` (time to flame) returned `CMD_ERROR` twice in the latest read, including a separate two-frame request. Historical success does not make them currently usable. Error payload `0001` is not a reading.
- Per-circuit heat demand is not automatically the same as circuit flow setpoint; the photographed HK2 values differ.
- VPT flow, boiler flow, and return sensors are distinct; no new interchangeability is assumed.
- Stored W10/W19 fault-memory entries do not establish an active fault.
- Boiler output percentage is not VPT thermal output in kW, and VPT heat output alone is not a burner ON signal.

## Validation boundaries and release checks

New regression tests cover field response decoding, error isolation with shuffled frames, zero values, unsigned ionisation, read-only setup, HK2-only mixer exposure and duplicate polling prevention. Existing tests cover six-frame limits, throttling, write settling and 0.4.7 registry behavior. Additional tests cover successful/failed unload, cancellation during a write or settle delay, stale-entity writes and persisted intervals. All 77 tests passed. A direct comparison against 0.4.7 confirmed that all 85 existing regular sensor definitions and 19 existing experimental register definitions are unchanged; device/entity preservation tests also pass. Local tests use Home Assistant stubs and do not substitute for a live installation test.

Original photographs and local time-series exports are not part of the public release. Local evidence is stored in ignored `local-diagnostics/`. No credentials or private network configuration are included in this document.

## Pull request review

PRs [#1](https://github.com/JS-DE-Tech/hacs-weishaupt-lan/pull/1) through [#8](https://github.com/JS-DE-Tech/hacs-weishaupt-lan/pull/8) were already merged when reviewed. Multi-circuit support, device grouping, raw-response matching, diagnostics and throttling are retained; no duplicate cherry-picks are necessary. Two outstanding PR #7 review findings are fixed in 0.5.0: pending write/refresh tasks are cancelled on successful entry unload, and old persisted polling intervals are clamped to the supported 30-600 second range.
