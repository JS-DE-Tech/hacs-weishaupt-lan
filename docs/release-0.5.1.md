# Version 0.5.1: installation and recovery

Minimum Home Assistant Core: **2026.8.0**, unchanged from 0.5.0.

## Offline startup

In 0.5.0 and earlier, discovery while a boiler was off or unreachable could produce an incomplete inventory and trigger deletion of registered device/entity entries. Version 0.5.1 verifies connectivity before discovery. Missing responses from previously registered devices cause setup to retry through Home Assistant's `ConfigEntryNotReady` mechanism. Probe results no longer authorize registry deletion, including when optional diagnostic groups are disabled.

If a device is permanently removed from the installation, its registry record must be reviewed and removed manually; a missing response alone is not proof of removal. Previously registered modules which do not answer keep setup pending. No actuator command is sent by these recovery checks.

For devices already missing after a 0.5.0 startup, switch the boiler on and reload the existing integration through Settings > Devices & services. Do not remove and re-add the integration. Recovery was verified on the reported installation under 0.5.0: the devices reappeared and the 102 previously recorded entity/unique-ID pairs were restored. That observation is not a live test of the new 0.5.1 code or a guarantee that deleted device customizations are restored on other installations.

## Update

1. Create a Home Assistant backup.
2. Update through HACS to 0.5.1 and restart Home Assistant.
3. Verify existing devices and operating values. Do not delete ConfigEntries or edit registry files.
4. The nine [owner-confirmed WTC readings](confirmed-wtc-readings.md) appear under the existing boiler device without EXP and without experimental options. At the owner's request these are new regular entities, with new IDs; the former extended EXP entries are no longer provided. Old registry/history records are not automatically deleted. Other existing entity identities are unchanged.
5. If the boiler was off during restart, Home Assistant should retry setup when it becomes reachable. Check the integration status and logs after connectivity returns.

## Validation boundaries

Automated tests use Home Assistant API stubs. They cover offline setup, recovery of the connection gate, retained registry records, known-device probe failures, fresh regular IDs, device assignment, preserved register decoding, valid zeros and unsigned ionisation values. No live boiler shutdown or live 0.5.1 installation was performed during development.

## Rollback

Restore the complete 0.5.0 component directory and restart Home Assistant, leaving ConfigEntries and registry data intact. The previous extended EXP entries are available again if their options are enabled; the new regular entries will not be provided by 0.5.0. Keep the boiler reachable during startup because 0.5.0 retains the offline-discovery defect.
