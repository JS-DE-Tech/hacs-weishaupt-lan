# Weishaupt Manual Reference Map

This document maps Weishaupt operating-manual information menu numbers to the
Home Assistant entities and CanApiJson register definitions that already exist
in this integration.

Manual information numbers such as `1.6.1` are Weishaupt UI/manual references.
They are not direct CanApiJson addresses. CanApiJson addresses are shown in
`MI/MX/OX/OS VS=n` format.

Existing confirmed mappings are based on the current integration code and the
real-hardware validation documented in [confirmed-registers.md](confirmed-registers.md).
Entries derived from the external `wem_codes.py` research reference are research
candidates only. Candidate values must be validated by targeted correlation
snapshots before they become regular sensors. No write support is derived from
`wem_codes.py`.

Some concrete candidates are exposed as experimental read-only sensors for
field validation. Values, scaling, value size, and interpretation must still be
verified on real hardware before they can be promoted to confirmed sensors.

Status values used in this document:

- `confirmed`: implemented in the integration and documented as confirmed or
  empirically confirmed.
- `probable`: implemented or correlated enough to be useful, but the exact
  manual-menu equivalence still needs care.
- `missing`: no confirmed current entity or register definition exists.
- `experimental candidate`: read-only candidate for later correlation only.
- `not applicable`: the manual entry is not represented as a read-only sensor.

## Heating Circuits

Heating-circuit mappings use the current circuit model:

| Circuit | Current entity key pattern | CanApiJson module |
|---|---|---|
| HK1 | `sg_*_hk1` and related SG keys | `02/00/...` |
| HK2 | `hk_*` | `02/01/...` |
| HK3 | `hk3_*`, dynamically derived from `hk_*` | `02/02/...` |

### HK1

| Manual Ref | Menu path | Description | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|---|
| `1.6.1` | Heizkreis 1 > Info > Betriebsart | Current operating mode | `sg_betriebsart_hk1_aktuell` (`Betriebsart HK1 aktuell`) | `02/00/257E/04 VS=1` | confirmed | Uses `BETRIEBSART_AKTUELL_MAP`. |
| `1.6.2` | Heizkreis 1 > Info > Status | Current heating-circuit status | `sg_status_hk1` (`Status HK1`) | `02/00/257E/05 VS=1` | confirmed | Uses `STATUS_HK_MAP`. |
| `1.6.3` | Heizkreis 1 > Info > Aussentemperatur / Aussentemperatur lokal | Outdoor temperature | `sg_aussentemperatur` (`Aussentemperatur`) | `01/00/26B1/02 VS=2` | probable | System outdoor temperature, scale `0.1 C`; no confirmed local-per-HK entity. |
| `1.6.4` | Heizkreis 1 > Info > Raumsolltemperatur | Current room target temperature | `sg_raumsolltemperatur_aktuell` (`Raumsolltemperatur aktuell`) | `02/00/2558/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.5` | Heizkreis 1 > Info > Vorlaufsolltemperatur | Current flow target temperature | `sg_vorlaufsolltemperatur_aktuell` (`Vorlaufsolltemperatur aktuell`) | `02/00/2559/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.6` | Heizkreis 1 > Info > Vorlaufisttemperatur | Current flow temperature | `sg_vorlaufisttemperatur` (`Vorlaufisttemperatur`) | `02/00/2507/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.7` | Heizkreis 1 > Info > Mischerstellung Soll | Mixer target position | `sg_hk1_candidate_mischerstellung_soll` (`Kandidat Mischerstellung Soll`) | `02/00/2536/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=2` may still be needed on some hardware and must be validated. |
| `1.6.8` | Heizkreis 1 > Info > Mischerstellung Ist | Mixer actual position | `sg_hk1_candidate_mischerstellung_ist` (`Kandidat Mischerstellung Ist`) | `02/00/254F/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=2` may still be needed on some hardware and must be validated. |
| `1.6.9` | Heizkreis 1 > Info > Pumpe Heizkreis | Heating-circuit pump state | `sg_hk1_candidate_pumpe_heizkreis` (`Kandidat Pumpe Heizkreis`) | `02/00/2546/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=1` is plausible for on/off; final VS needs hardware confirmation. |
| `1.6.10` | Heizkreis 1 > Info > Korrektur Aufheizoptimierung | Heat-up optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |
| `1.6.11` | Heizkreis 1 > Info > Korrektur Absenkoptimierung | Setback optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |

### HK2

| Manual Ref | Menu path | Description | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|---|
| `1.6.1` | Heizkreis 2 > Info > Betriebsart | Current operating mode | `hk_betriebsart_aktuell` (`HK Betriebsart aktuell`) | `02/01/257E/04 VS=1` | confirmed | Uses `BETRIEBSART_AKTUELL_MAP`. |
| `1.6.2` | Heizkreis 2 > Info > Status | Current heating-circuit status | `hk_status` (`HK Status`) | `02/01/257E/05 VS=1` | confirmed | Uses `STATUS_HK_MAP`. |
| `1.6.3` | Heizkreis 2 > Info > Aussentemperatur / Aussentemperatur lokal | Outdoor temperature | none | candidate family, see research section | experimental candidate | Local/mixed/damped FBH outdoor-temperature candidates need correlation. |
| `1.6.4` | Heizkreis 2 > Info > Raumsolltemperatur | Current room target temperature | `hk_raumsolltemperatur_aktuell` (`HK Raumsolltemperatur aktuell`) | `02/01/2558/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.5` | Heizkreis 2 > Info > Vorlaufsolltemperatur | Current flow target temperature | `hk_vorlaufsolltemperatur_aktuell` (`HK Vorlaufsolltemperatur aktuell`) | `02/01/2559/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.6` | Heizkreis 2 > Info > Vorlaufisttemperatur | Current flow temperature | `hk_vorlaufisttemperatur` (`HK Vorlaufisttemperatur`) | `02/01/2507/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.6.7` | Heizkreis 2 > Info > Mischerstellung Soll | Mixer target position | `hk_mischerstellung_soll` (`HK Mischerstellung Soll`) | `02/01/2536/02 VS=1` | confirmed | Correlated with the physical display; VS=1, raw percent. See field-validation-0.5.0.md. |
| `1.6.8` | Heizkreis 2 > Info > Mischerstellung Ist | Mixer actual position | `hk_mischerstellung_ist` (`HK Mischerstellung Ist`) | `02/01/254F/02 VS=1` | confirmed | Correlated with the physical display; VS=1, raw percent. See field-validation-0.5.0.md. |
| `1.6.9` | Heizkreis 2 > Info > Pumpe Heizkreis | Heating-circuit pump state | `hk_candidate_pumpe_heizkreis` (`HK Kandidat Pumpe Heizkreis`) | `02/01/2546/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=1` is plausible for on/off; final VS needs hardware confirmation. |
| `1.6.10` | Heizkreis 2 > Info > Korrektur Aufheizoptimierung | Heat-up optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |
| `1.6.11` | Heizkreis 2 > Info > Korrektur Absenkoptimierung | Setback optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |

### HK3

| Manual Ref | Menu path | Description | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|---|
| `1.6.1` | Heizkreis 3 > Info > Betriebsart | Current operating mode | `hk3_betriebsart_aktuell` (`HK3 Betriebsart aktuell`) | `02/02/257E/04 VS=1` | confirmed | Built from the HK definition with `MX=0x02`; uses `BETRIEBSART_AKTUELL_MAP`. |
| `1.6.2` | Heizkreis 3 > Info > Status | Current heating-circuit status | `hk3_status` (`HK3 Status`) | `02/02/257E/05 VS=1` | confirmed | Built from the HK definition with `MX=0x02`; uses `STATUS_HK_MAP`. |
| `1.6.3` | Heizkreis 3 > Info > Aussentemperatur / Aussentemperatur lokal | Outdoor temperature | none | candidate family, see research section | experimental candidate | Local/mixed/damped outdoor-temperature candidates need HK3 correlation. |
| `1.6.4` | Heizkreis 3 > Info > Raumsolltemperatur | Current room target temperature | `hk3_raumsolltemperatur_aktuell` (`HK3 Raumsolltemperatur aktuell`) | `02/02/2558/02 VS=2` | confirmed | Built from the HK definition with `MX=0x02`; scale `0.1 C`, signed. |
| `1.6.5` | Heizkreis 3 > Info > Vorlaufsolltemperatur | Current flow target temperature | `hk3_vorlaufsolltemperatur_aktuell` (`HK3 Vorlaufsolltemperatur aktuell`) | `02/02/2559/02 VS=2` | confirmed | Built from the HK definition with `MX=0x02`; scale `0.1 C`, signed. |
| `1.6.6` | Heizkreis 3 > Info > Vorlaufisttemperatur | Current flow temperature | `hk3_vorlaufisttemperatur` (`HK3 Vorlaufisttemperatur`) | `02/02/2507/02 VS=2` | confirmed | Built from the HK definition with `MX=0x02`; scale `0.1 C`, signed. |
| `1.6.7` | Heizkreis 3 > Info > Mischerstellung Soll | Mixer target position | `hk3_candidate_mischerstellung_soll` (`HK3 Kandidat Mischerstellung Soll`) | `02/02/2536/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=2` may still be needed on some hardware and must be validated. |
| `1.6.8` | Heizkreis 3 > Info > Mischerstellung Ist | Mixer actual position | `hk3_candidate_mischerstellung_ist` (`HK3 Kandidat Mischerstellung Ist`) | `02/02/254F/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=2` may still be needed on some hardware and must be validated. |
| `1.6.9` | Heizkreis 3 > Info > Pumpe Heizkreis | Heating-circuit pump state | `hk3_candidate_pumpe_heizkreis` (`HK3 Kandidat Pumpe Heizkreis`) | `02/02/2546/02 VS=1` | experimental candidate | Exposed only when experimental HK candidate sensors are enabled. `VS=1` is plausible for on/off; final VS needs hardware confirmation. |
| `1.6.10` | Heizkreis 3 > Info > Korrektur Aufheizoptimierung | Heat-up optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |
| `1.6.11` | Heizkreis 3 > Info > Korrektur Absenkoptimierung | Setback optimization correction | none | unknown | missing | No current confirmed entity or candidate address. |

## Warm Water

| Manual Ref | Menu path | Description | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|---|
| `1.7.1` | Warmwasser > Info > Status | Domestic-hot-water status | `sg_status_warmwasser` (`Status Warmwasser`) | `03/00/2569/02 VS=1` | confirmed | Uses `STATUS_WW_MAP`. |
| `1.7.3` | Warmwasser > Info > Warmwassersolltemperatur | Current domestic-hot-water target temperature | `sg_wwsolltemperatur_aktuell` (`WW-Solltemperatur aktuell`) | `03/00/252C/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.7.4` | Warmwasser > Info > Warmwassertemperatur | Current domestic-hot-water temperature | `sg_warmwassertemperatur` (`Warmwassertemperatur`) | `03/00/2529/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.7.5` | Warmwasser > Info > Ruecklauftemperatur Zirkulation | Circulation return temperature | `sg_ruecklauftemperatur_zirkulation` (`Ruecklauftemperatur Zirkulation`) | `03/00/2557/02 VS=2` | confirmed | Scale `0.1 C`, signed. |
| `1.7.6` | Warmwasser > Info > Pumpe Warmwasser | Domestic-hot-water pump | `sg_pumpe_warmwasser` (`Pumpe Warmwasser`) | `03/00/2551/02 VS=1` | confirmed | Uses `PUMPE_MAP`. |

## WTC

| Manual Ref | Menu path | Description | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|---|
| `1.2.1.1` | WTC > Info > Betriebsphase WTC | WTC operating phase | `wtc_betriebsphase` (`Betriebsphase WTC`) | `09/01/2639/00 VS=1` | confirmed | Uses `BETRIEBSPHASE_WTC_MAP`. |
| `1.2.1.2` | WTC > Info > Betriebsphase Brenner | Burner operating phase | `wtc_betriebsphase_brenner` (`Betriebsphase Brenner`) | `07/00/2541/00 VS=1` | confirmed | Uses `BETRIEBSPHASE_BRENNER_MAP`. |
| `1.2.1.3` | WTC > Info > Sollleistung | Requested burner output | none | candidate family, see research section | experimental candidate | Do not equate this with `wtc_waermeleistung_vpt`, which is kW heat output. |
| `1.2.1.4` | WTC > Info > Istleistung | Actual burner output | none | candidate family, see research section | experimental candidate | Do not equate this with `wtc_waermeleistung_vpt`, which is kW heat output. |
| n/a | WTC > Info > Kesseltemperatur | Boiler temperature | `wtc_kesseltemperatur` (`Kesseltemperatur`) | `07/00/2532/00 VS=2` | confirmed | Scale `0.1 C`, signed. |
| n/a | WTC > Info > Anlagendruck | System pressure | `wtc_anlagendruck` (`Anlagendruck`) | `09/01/2614/02 VS=2` | confirmed | Scale `0.01 bar`. |
| n/a | WTC > Info > Abgastemperatur | Flue-gas temperature | `wtc_abgastemperatur` (`WTC Abgastemperatur`) | `07/00/2533/02 VS=2` | confirmed | Empirically confirmed; scale `0.1 C`, signed. |
| n/a | WTC > Info > Ruecklauftemperatur | Return temperature | `wtc_ruecklauftemperatur` (`WTC Ruecklauftemperatur`) | `07/00/2537/00 VS=2` | confirmed | Empirically confirmed; scale `0.1 C`, signed. |
| n/a | WTC > Info > Volumenstrom VPT | VPT volume flow | `wtc_volumenstrom_vpt` (`Volumenstrom VPT`) | `09/01/2613/02 VS=2` | confirmed | Unit `l/h`; raw `0` is valid. |
| n/a | WTC > Info > Waermeleistung VPT | VPT thermal output | `wtc_waermeleistung_vpt` (`Waermeleistung VPT`) | `09/01/2631/02 VS=4` | confirmed | Scale `0.01 kW`; probed with `VS=4` and `VS=2` fallback. Not WTC percentage output. |
| n/a | WTC > Info > Brennerstarts gesamt | Burner starts total | `wtc_brennerstarts_gesamt` (`Burner Starts Total`) | `09/01/2920/00 VS=2` | confirmed | Uses only the selected confirmed mirror address. |
| n/a | WTC > Info > Betriebsstunden gesamt | Burner operating hours total | `wtc_betriebsstunden_gesamt` (`Burner Operating Hours Total`) | `09/01/2921/00 VS=2` | confirmed | Unit `h`; uses only the selected confirmed mirror address. |
| n/a | WTC > Info > Zeit bis Wartung | Remaining time until maintenance | `wtc_zeit_bis_wartung` (`Zeit bis Wartung`) | `09/01/2641/00 VS=2` | confirmed | Empirically confirmed; diagnostic, disabled by default. |
| n/a | WTC > Info > Wartungsintervall | Maintenance interval | `wtc_wartungsintervall` (`Wartungsintervall`) | `09/01/2642/00 VS=2` | confirmed | Empirically confirmed; diagnostic, disabled by default. |

## Systemgeraet Date/Time

The known Systemgeraet date/time component registers are confirmed readable via
`SRC=DDC` and are exposed by the integration as derived read-only diagnostic
entities:

| Component | Current HA entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|
| Uhrzeit Stunden | `sg_device_clock_time` (`Uhrzeit Anlage`) | `01/00/2562/02 VS=1` | confirmed | Source component for the derived clock-time sensor. |
| Uhrzeit Minuten | `sg_device_clock_time` (`Uhrzeit Anlage`) | `01/00/2562/03 VS=1` | confirmed | Source component for the derived clock-time sensor. |
| Datum Jahr | `sg_device_date` (`Datum Anlage`) | `01/00/2563/02 VS=1` | confirmed | Year encoding is a two-digit year; `26` means `2026`. |
| Datum Monat | `sg_device_date` (`Datum Anlage`) | `01/00/2563/03 VS=1` | confirmed | Source component for the derived date sensor. |
| Datum Tag | `sg_device_date` (`Datum Anlage`) | `01/00/2563/04 VS=1` | confirmed | Source component for the derived date sensor. |

### Real-Hardware Write Tests

| Test | Request | Meaning | Response | Result | Notes |
|---|---|---|---|---|---|
| Year write | `03 01 00 2563 02 0001 1a` | `SET 01/00/2563/02 VS=1 value=26` | `05 01 00 2563 02 0002 0001` | `CMD_ERROR` | Normal `CMD_SET` was rejected. |
| Minute write as single byte | `03 01 00 2562 03 0001 0a` | `SET 01/00/2562/03 VS=1 value=10` | `05 01 00 2562 03 0002 0001` | `CMD_ERROR` | Normal `CMD_SET` was rejected. |
| Combined hour/minute write as two-byte object | `03 01 00 2562 02 0002 100d` | `SET 01/00/2562/02 VS=2 value=16:13` | `05 01 00 2562 02 0002 0001` | `CMD_ERROR` | Normal `CMD_SET` was rejected. |

### Systemgeraet Date/Time Conclusion

- `sg_device_clock_time` and `sg_device_date` remain read-only.
- The known Systemgeraet date/time registers are confirmed readable through
  CanApiJson.
- Write access using normal `CMD_SET` is rejected by the device.
- Automatic Systemgeraet time synchronization is not implemented.
- A `Zeitabgleich` switch must not be created.
- A `Zeit-Sync` button must not be created.
- The known date/time registers must not be used for periodic writes.
- A future implementation requires discovery of another writable time-setting
  parameter or another supported synchronization mechanism.

## Research Candidates From `wem_codes.py`

The external [wem_codes.py research reference](https://github.com/geronet1/wem-python/blob/main/wem_codes.py) was inspected for release 0.5.0. Its labels and scales remain research candidates unless corroborated with the local device display. Current GET readability, response widths and validation limits are recorded in [field-validation-0.5.0.md](field-validation-0.5.0.md).

Older WEM/CAN group hints mentioned by the request:

| Group hint | Area | Status | Notes |
|---|---|---|---|
| `0x582` | WTC | experimental candidate | Older WEM grouping only; not a CanApiJson confirmation by itself. |
| `0x583` | Heizkreis | experimental candidate | Older WEM grouping only; useful for later HK correlation planning. |
| `0x584` | Solar | experimental candidate | Older WEM grouping only; no manual-reference mapping added here. |

### Heating-Circuit Research Candidates

The broad address hypotheses below are retained as research context. HK2 mixer target/actual at MX=01, VS=1 are now confirmed; use the normal `hk_mischerstellung_soll` and `hk_mischerstellung_ist` definitions above. Other mixer addresses and pump OFF remain subject to field validation.

| Manual Ref | Candidate label | HA sensor/entity | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|
| `1.6.7` | Mischerstellung Soll FBH | none | `02/00/2536/02`, `02/01/2536/02`, `02/02/2536/02` | experimental candidate | Possible mixer target position. `VS=1` may be sufficient for percentages; `VS=2` may be needed for two-byte numeric values. |
| `1.6.8` | Mischerstellung Ist FBH | none | `02/00/254F/02`, `02/01/254F/02`, `02/02/254F/02` | experimental candidate | Possible mixer actual position. `VS=1` may be sufficient for percentages; `VS=2` may be needed for two-byte numeric values. |
| `1.6.9` | Pumpe Heizkreis FBH | none | `02/00/2546/02`, `02/01/2546/02`, `02/02/2546/02` | experimental candidate | Possible pump state. `VS=1` may be sufficient for on/off; final VS must be confirmed. |
| `1.6.3` | Aussentemperatur lokal Gemittelt FBH | none | unknown | experimental candidate | Candidate label only from request context; address not supplied. |
| `1.6.3` | Aussentemperatur lokal Gemischt FBH | none | unknown | experimental candidate | Candidate label only from request context; address not supplied. |
| `1.6.3` | Aussentemperatur Aktuell FBH | `sg_aussentemperatur` may cover the system value | `01/00/26B1/02 VS=2` for system value | experimental candidate | Per-HK local value remains unconfirmed. |
| `1.6.4` | Raumsolltemperatur Aktuell FBH | `hk_raumsolltemperatur_aktuell` / `hk3_raumsolltemperatur_aktuell` | `02/01/2558/02 VS=2`, `02/02/2558/02 VS=2` | confirmed | Existing HK2/HK3 definitions already cover current room target temperature. |
| `1.6.5` | Vorlaufsolltemperatur Aktuell FBH | `hk_vorlaufsolltemperatur_aktuell` / `hk3_vorlaufsolltemperatur_aktuell` | `02/01/2559/02 VS=2`, `02/02/2559/02 VS=2` | confirmed | Existing HK2/HK3 definitions already cover current flow target temperature. |
| n/a | Waermeanforderung Heizkreis FBH | none | unknown | experimental candidate | Candidate label only from request context; likely needs separate targeted snapshots. |

### WTC Research Candidates

| Manual Ref | Candidate label | Existing related entity/candidate | CanApiJson address | Status | Notes |
|---|---|---|---|---|---|
| `1.2.1.3` | Sollleistung WE0 | none | unknown | experimental candidate | Possible percentage-based requested output; do not map to kW `wtc_waermeleistung_vpt`. |
| `1.2.1.4` | Leistung / Istleistung | none | unknown | experimental candidate | Possible percentage-based actual output; do not map to kW `wtc_waermeleistung_vpt`. |
| `1.2.2.2` | Pumpenleistung Pumpe intern Sollleistung WE0 | `wtc_candidate_pumpe_intern_sollleistung` (`Kandidat Pumpenleistung Pumpe intern Sollleistung`) | `09/01/2619/02 VS=1` | experimental candidate | Exposed through the extended experimental WTC option for field validation. Same address remains available as a curated raw diagnostic candidate. |
| n/a | Pumpenleistung Pumpe intern Elektrische Leistung WE0 | none | unknown | experimental candidate | Candidate label only from request context. |
| `1.2.1.4` | Geblaese-Ansteuersignal Aktuell WE0 | `wtc_candidate_geblaese_ansteuersignal` | `07/00/257E/00 VS=2` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| `1.2.1.4` | Geblaesedrehzahl Aktuell WE0 | `wtc_candidate_geblaesedrehzahl` | `07/00/2540/00 VS=2` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| `1.2.1.4` | Gasventil Ansteuersignal Aktuell WE0 | `wtc_candidate_gasventil_ansteuersignal` | `07/00/253F/00 VS=2` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Gas-Luft-Verhaeltnis Aktuell WE0 | `wtc_candidate_gas_luft_verhaeltnis` | `07/00/257D/00 VS=2` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Ionisationssignal Start WE0 | `wtc_candidate_ionisation_start` | `07/00/257A/00 VS=1` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Ionisationssignal Sollwert WE0 | `wtc_candidate_ionisation_soll` | `07/00/2579/00 VS=1` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Ionisationssignal SCOT-Istwert WE0 | `wtc_candidate_ionisation_scot_ist` | `07/00/2539/00 VS=1` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Ionisationssignal SCOT-Basiswert WE0 | `wtc_candidate_ionisation_scot_basis` | `07/00/253A/00 VS=1` | experimental candidate | Readable in targeted GETs; opt-in diagnostics only. Meaning/scaling still require simultaneous display correlation. |
| n/a | Zeit bis Flammenbildung Aktuell WE0 | none | `07/00/257B/00 VS=2` | unsupported in latest GET | CMD_ERROR twice; excluded from 0.5.0 candidates. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2610_02_02` | `09/01/2610/02 VS=2` | experimental candidate | Current code hint: unconfirmed temperature-related WTC value, probable scale `0.1 C`. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2611_02_02` | `09/01/2611/02 VS=2` | experimental candidate | Current code hint: unconfirmed temperature-related WTC value, probable scale `0.1 C`. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2612_02_02` | `09/01/2612/02 VS=2` | experimental candidate | Current code hint: unconfirmed temperature-related WTC value, probable scale `0.1 C`. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2615_02_02` | `09/01/2615/02 VS=2` | experimental candidate | Current code hint: likely VPT flow temperature, probable scale `0.1 C`. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_263a_02_02` | `09/01/263A/02 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2679_00_02` | `09/01/2679/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268a_00_04` | `09/01/268A/00 VS=4` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268b_00_04` | `09/01/268B/00 VS=4` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268c_00_04` | `09/01/268C/00 VS=4` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268d_00_02` | `09/01/268D/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268e_00_02` | `09/01/268E/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_268f_00_02` | `09/01/268F/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2902_00_02` | `09/01/2902/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2903_00_02` | `09/01/2903/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2904_00_01` | `09/01/2904/00 VS=1` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2905_00_01` | `09/01/2905/00 VS=1` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2908_00_02` | `09/01/2908/00 VS=2` | experimental candidate | Existing raw diagnostics candidate. |
| n/a | Existing curated WTC candidate | `wtc_experimental_09_01_2922_00_01` | `09/01/2922/00 VS=1` | experimental candidate | Existing raw diagnostics candidate. |

## Next Correlation Targets

1. `1.6.7` Mischerstellung Soll
2. `1.6.8` Mischerstellung Ist
3. `1.6.9` Pumpe Heizkreis
4. `1.2.1.3` Sollleistung
5. `1.2.1.4` Istleistung
6. Geblaese-Ansteuersignal
7. Geblaesedrehzahl
8. Gasventil-Ansteuersignal
9. Ionisationssignal
10. Pumpenleistung intern
11. Systemgeraet writable time-setting mechanism
