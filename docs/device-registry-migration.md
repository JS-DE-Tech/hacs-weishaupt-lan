# Home Assistant device registry API migration

## Scope and compatibility

This change only migrates device registry APIs. It does not change register
addresses, CanApiJson requests, heating commands, polling, sensor conversions,
entity unique IDs, entity IDs or saved integration configuration. The domain
remains `weishaupt_wtc_lan` and the manifest version is `0.4.7`.

The required API minimum is Home Assistant Core **2026.8.0**. The relevant
signatures were checked in the official Core 2026.8.0 and 2026.9.4 sources.
Earlier Core versions are not supported by this code. The minimum is declared
in `hacs.json`; the integration manifest does not declare a Core minimum and
only its integration version is bumped. Manual installations must check the
Core version themselves.

Home Assistant introduced ConfigEntry-scoped device identifiers in 2026.8.
The deprecated `via_device` and `async_get_device()` APIs are scheduled for
removal in 2027.8. This migration removes those usages but does not claim that
all unrelated APIs have been tested against future Core releases.

Official references:

- [ConfigEntry-scoped device registry and deprecations](https://developers.home-assistant.io/blog/2026/07/21/device-registry-single-config-entry/)
- [Follow-up changes and parent device IDs](https://developers.home-assistant.io/blog/2026/08/24/device-registry-follow-up-changes/)
- [Core 2026.8.0 device registry source](https://github.com/home-assistant/core/blob/2026.8.0/homeassistant/helpers/device_registry.py)
- [Core 2026.9.4 device registry source](https://github.com/home-assistant/core/blob/2026.9.4/homeassistant/helpers/device_registry.py)

## Existing devices and configuration

Every entity platform first registers or retrieves the Systemgeraet using its
unchanged identifier and the owning ConfigEntry. The returned `DeviceEntry.id`
is kept on the coordinator. Child devices reference that actual registry ID
through `via_device_id`, including the experimental diagnostics device. This
works regardless of which platform is set up first.

Inactive-device cleanup uses `async_get_device_by_identifier(identifier,
config_entry_id)` so a matching identifier owned by another ConfigEntry is not
selected. Existing foreign-entity cleanup protections remain in place.

No integration storage migration, ConfigEntry replacement, entity renaming or
device recreation is required. Existing user names, areas, disabled settings
and stable device links are reused. An unchanged installation should have the
same device/entity counts after restart or reload. Newly detected devices and
the existing inactive-device cleanup can still change counts independently of
this API migration.

Core itself can split formerly shared devices when upgrading to the newer
registry model. That Core migration is distinct from this integration change;
this code does not undo it or merge devices belonging to separate ConfigEntries.

## Install on an existing Home Assistant instance

1. Create a full Home Assistant backup and keep a copy of the currently installed
   `/config/custom_components/weishaupt_wtc_lan` directory. Record the Core
   version and current device/entity counts, IDs, areas and disabled settings.
2. Confirm Core is at least 2026.8.0. For the reported environment, use 2026.9.4.
3. Replace the installed component directory with the complete patched
   `custom_components/weishaupt_wtc_lan` directory from this repository, or
   update to v0.4.7 through HACS.
4. Restart Home Assistant to load the changed Python modules. Do not remove
   and re-add the integration, delete its devices, or edit `.storage` files.
5. Follow the checks below, then reload the existing integration through
   Settings > Devices & services and repeat the device/ID checks.

## Validation and remaining limits

Local validation uses the repository's bundled-Python unittest suite and
Home Assistant API stubs, not a running Core instance or a connected boiler.
The suite covers:

- First entity-platform setup in all 24 sensor/select/number/button orders.
- Existing registry IDs and user settings across two simulated reloads.
- ConfigEntry ownership when another entry has the same device identifier.
- Existing entity IDs/settings and device associations in a simulated registry.
- Pressure and temperature readings, domestic-hot-water targets, heating-circuit
  operating modes and unchanged select/number/button write-queue arguments.
- Existing protocol, ACK validation, configuration and parsing regressions.

Run on the development checkout:

```text
python -m compileall custom_components tests
python -m unittest discover -s tests -v
git diff --check
```

A real Core 2026.9.4 installation with its persisted registries still needs the
following acceptance checks. The local tests do not substitute for these:

1. Compare devices, parent links, entity IDs, user names, areas and disabled
   settings with the pre-update record. Check automations and history still
   reference the same entities, with no duplicate devices or entities.
2. Check sensor values against the local Systemgeraet UI and confirm current
   operating modes and configured targets are displayed correctly.
3. If safe for the heating installation, make one controlled target/mode change
   and restore the original value. Verify acknowledgement and subsequent
   readings. Local tests only simulate these writes; no hardware commands were
   sent during development.
4. Reload the existing ConfigEntry and confirm unchanged IDs and hierarchy.
5. Check logs for setup errors and confirm this integration no longer emits
   warnings for `via_device` or `DeviceRegistry.async_get_device()`.

## Rollback

1. Restore the saved, complete previous component directory at
   `/config/custom_components/weishaupt_wtc_lan` and restart Home Assistant.
   Leave ConfigEntries, device/entity registries and options intact; no reverse
   integration storage migration is needed.
2. Recheck IDs, device assignments and values. The previous code can emit the
   original deprecation warnings. Code using the removed APIs is not a suitable
   rollback on Core 2027.8 or later.
3. If the problem involves a Core upgrade or its own registry migration, use a
   coherent full backup and the matching prior Core version. Replacing only
   integration code does not reverse Core's storage migrations. Full-backup
   recovery can discard changes made after the backup, so preserve any needed
   newer configuration separately before recovery.

Do not delete the integration, reset device/entity registries, or manually edit
`.storage` as a rollback technique.
