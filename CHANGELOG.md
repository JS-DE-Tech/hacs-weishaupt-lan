# Changelog

## 0.5.1 - 2026-11-23

### Changed
- Promote the nine owner-confirmed combustion and internal-pump readings to regular read-only sensors on the boiler device, without EXP labels or experimental opt-in.
- Create fresh regular identities for these nine sensors at the owner's explicit request. Other existing entity identities remain unchanged; old EXP registry/history records are not automatically deleted.
- Record owner confirmation separately from historical independent field measurements in `docs/confirmed-wtc-readings.md`.

### Fixed
- Retry setup when the boiler is unreachable instead of creating a partial device inventory.
- Retain registered devices and entities when discovery is incomplete or returns an error. Previously known devices that stop responding cause setup to retry instead of being deleted.
- Add regression coverage for offline startup, restored connectivity and registry preservation. Disabling optional diagnostics also retains their registry records.

## 0.5.0 - 2026-11-23

### Added
- Added normal read-only HK2 mixer target and actual position sensors, correlated with the local device display.
- Added regular read-only HK2/HK3 pump status sensors on their existing heating-circuit devices. Pump ON has been observed; the existing OFF mapping remains to be field-validated.
- Added opt-in HK1 pump and unconfirmed HK1/HK3 mixer diagnostics. New experimental display names use the EXP prefix.
- Added eight named combustion candidates to extended experimental WTC diagnostics: fan speed/control, gas-valve control, gas/air ratio, and four ionisation signals.
- Added the internal pump modulation candidate and documented its remaining validation limits.
- Added field-validation evidence and manual menu mapping; raw zero remains a valid reading.

### Fixed
- Cancel pending writes and delayed refreshes when an entry unloads; reject writes from stale entities. Addresses the outstanding review in PR #7.
- Clamp persisted polling intervals to 30-600 seconds when creating the coordinator, including older stored configurations (PR #7 review).
- Keep unsigned combustion candidates unsigned rather than interpreting their high bit as a negative value.
- Avoid duplicate HK2 mixer candidates and avoid adding HK1 candidates when HK1 is absent.

### Notes
- Combustion candidates are disabled by default and remain read-only diagnostics until simultaneous display comparison confirms meaning and scaling.
- Gas-valve offset and time-to-flame returned CMD_ERROR in the latest probe and are not exposed as new sensors.
- Existing 0.4.7 device-registry migration, identifiers, controls and request throttling are retained. All 85 existing regular and 19 experimental register definitions compare unchanged against 0.4.7.
- Local tests use Home Assistant stubs; the live installation has not been upgraded to 0.5.0.

## 0.4.7 - 2026-10-01

### Fixed
- Migrated device hierarchy links to real `via_device_id` registry IDs and scoped device lookups to the owning ConfigEntry.
- Preserved existing device identifiers, entity IDs, user settings and heating controls on setup and reload.

### Changed
- Raised the minimum Home Assistant Core version to 2026.8.0 for the required device registry APIs.
- Documented installation, real-instance validation and rollback for existing integrations.

## 0.4.6 - 2026-06-12

### Changed
- Serialized all CanApiJson HTTP requests through one shared client lock with a 300 ms minimum inter-request gap.
- Raised the configurable polling interval range to 30-600 seconds in 10-second steps.
- Queued writable entity updates centrally, coalesced rapid same-register changes, and delayed one coordinator refresh until after a 10-second post-write settling period.
- Documented polling recommendations: 30 seconds for normal operation, 60 seconds or slower with curated experimental sensors, and 120 seconds or slower with extended experimental diagnostics.

### Fixed
- Preserved last-good dynamic values when a later read batch fails, so unrelated entities do not become unavailable because one batch timed out.
- Reflected strictly acknowledged configured target values optimistically without fabricating actual-state mirrors.

## 0.4.5 - 2026-06-12

### Added
- Added total burner-start counter for the WTC boiler.
- Added total burner operating-hours counter for the WTC boiler.
- Added optional read-only `WTC Experimental Diagnostics` device.
- Added selected raw WTC register candidates for real-hardware correlation testing.
- Added diagnostic attributes with raw and scaled values.
- Added separate derived Systemgeraet device date and clock-time diagnostic sensors, enabled by default.
- Added read-only `Weishaupt Systemgeraet Netzwerk` device for confirmed static IPv4, device-name, certificate-CN, and MAC-address diagnostics when supported.
- Added empirically confirmed WTC maintenance diagnostics: remaining time until maintenance and maintenance interval.
- Added detected heating-circuit display names from `systable.csv` with editable override fields.
- Added real `M02_*.BIN;<display name>;<circuit number>` systable parsing and optional logical device display names from `M01`, `M03`, `M06`, and `M07` rows.
- Added persisted parsed detected-name mapping separate from manual heating-circuit name overrides.
- Added read-only `weishaupt_wtc_lan.export_local_metadata` service for troubleshooting local metadata parsing.
- Added read-only `Systembetriebsart aktuell` mirror sensor derived from the existing system operating-mode register.
- Added optional extended experimental WTC catalog infrastructure, capped at 100 explicitly listed entities and disabled by default.
- Added `weishaupt_wtc_lan.export_experimental_snapshot` service to export JSON and CSV correlation snapshots.

### Changed
- Kept CanApiJson read batches limited to six frames for improved reliability.
- Kept experimental polling disabled by default.
- Probed `wtc_waermeleistung_vpt` adaptively with `VS=4` first and `VS=2` fallback for devices that use a shorter response.
- Added confidence, probable-unit and probable-scale metadata for selected experimental WTC candidates.
- Network diagnostics are read immediately during setup/reload, refreshed at most once every 10 minutes, and kept as last-good cached coordinator data.
- Retained the historic HK2 technical key prefix `hk_` for backward compatibility.

### Fixed
- Preserved valid raw zero values in regular and experimental read paths.
- Ensured that a failing experimental register does not discard valid values from the same batch.
- Preserved `0.0 kW` as a valid WTC VPT thermal-output value.
- Corrected the validated Systemgeraet date-byte order: year, month, day.
- Removed redundant read-only HK2/HK3 operating-mode target sensors while keeping writable selects.
- Corrected confirmed network IP-mode labels: raw `1` is `Manuell`, raw `3` is `Automatisch (DHCP)`.
- Replaced the previous optional hostname probe with the confirmed read-only `06/00/250E/00 VS=16 GETS` device-name query; `06/00/2505/00` is not used.
- Skipped derived MAC-address diagnostics safely when any confirmed MAC component is missing.
- Kept the network device display name fixed as `Weishaupt Systemgeraet Netzwerk` while exposing the native Home Assistant configuration URL.

## 0.4.1 - 2026-06-10

- Fix: Limit automatic CanApiJson read batches to six VG frames and keep dense `N01`, `N02`, ... numbering in every batch.
- Fix: Treat raw value `0` as a valid measurement value, including WTC volume flow.
- Fix: Ensure `HK3 Betriebsart Vorgabe` and `Systembetriebsart` selects read their current state directly from `coordinator.data`.
- Fix: Keep HK1, HK2 and HK3 current operating-mode and status sensors while exposing only writable Vorgabe registers as controls.
- Fix: Use `/sd/systable.csv` as the primary read-only module inventory for optional device groups and avoid creating Solar when the module is missing.
- Feature: Add read-only `tools/probe_weishaupt_registers.py` for the empirically confirmed HK, system and WTC registers.
- Note: WTC registers 167 (`wtc_abgastemperatur`) and 168 (`wtc_ruecklauftemperatur`) are empirically confirmed.
- Note: No permanent warm-water on/off switch is created; `sg_warmwasser_push` remains a one-shot button only.

## 0.4.0 - 2026-06-09

- Feature: Move HK1 entities to a separate logical Home Assistant device while preserving their existing keys, CanApiJson addresses and unique IDs.
- Feature: Move warm-water entities and the existing Warmwasser-Push button to a separate `Weishaupt Warmwasser` device.
- Feature: Add writable `Systembetriebsart` select for Standby, Sommer and Automatik.
- Feature: Add Number slider entities for `WW-Solltemperatur Normal` (50-60 °C) and `WW-Solltemperatur Absenk` (8-60 °C), using the existing confirmed temperature registers.
- Feature: Register the Number platform and extend the scan interval slider to 10-600 seconds in 10 second steps.
- Feature: Detect optional WTC, warm-water and solar groups during setup/reload; Solar is not created when its known registers are missing or only return sentinel values.
- Feature: Add read-only `tools/dump_weishaupt_metadata.py` for local metadata inspection when investigating unconfirmed warm-water or maintenance registers.
- Fix: Reject write ACKs that contain an unexpected value payload.
- Migration: HK1 now uses the stable `<entry_id>_hk1` device identifier. Warm-water uses `<entry_id>_ww`. Existing entity unique IDs remain based on the original technical keys.
- Note: No clearly confirmed permanent warm-water on/off register or warm-water operating-mode register was found, so no Switch or additional WW operating-mode Select is created. Maintenance data is not available through the currently documented registers.
- Note: `wtc_abgastemperatur` remains on the WTC device and continues to treat `0x8000` and `0xFFFF` as unavailable.

## 0.3.0 - 2026-06-09

- Feature: Detect external EM-HK heating circuits dynamically and support HK1, HK2 and HK3 without creating entities for circuits that do not answer the CanApiJson probe.
- Feature: Add writable Betriebsart Vorgabe selects for every detected heating circuit.
- Feature: Add configurable heating circuit display names and an options flow with automatic reload.
- Feature: Replace the scan interval number field with a Home Assistant slider from 30 to 300 seconds in 10 second steps.
- Fix: Accept write operations only after a matching CanApiJson `CMD_ACK`; `CMD_ERROR`, missing responses and `CMD_RESPONSE` are rejected.
- Migration: HK2 keeps the historical `hk_*` sensor keys and `<entry_id>_hk` device identifier. HK3 uses new `hk3_*` keys and `<entry_id>_hk3`.
