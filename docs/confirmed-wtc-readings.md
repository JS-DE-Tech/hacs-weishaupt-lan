# Owner-confirmed WTC readings

On 2026-11-23 the installation owner explicitly confirmed the nine displayed readings below. This is an owner confirmation, not a claim that development independently repeated simultaneous physical-display measurements across the full operating range. The screenshot is retained privately; no personal installation data or image is published here.

## Regular read-only sensors

The readings belong to the existing WTC boiler device, without EXP in their names, and are available independently of both experimental WTC options. They keep the existing addresses, units and scale factors. A zero value remains valid. Error sentinels do not become measurements.

| Regular key | Name | MI/MX/OX/OS | VS | Scale/unit | Owner screenshot |
|---|---|---|---|---|---|
| `wtc_pumpe_intern_sollleistung` | Pumpenleistung Pumpe intern Sollleistung | `09/01/2619/02` | 1 | 1 % | 100 % |
| `wtc_geblaesedrehzahl` | Gebläsedrehzahl | `07/00/2540/00` | 2 | 1 rpm | 0 rpm |
| `wtc_geblaese_ansteuersignal` | Gebläse-Ansteuersignal | `07/00/257E/00` | 2 | 0.01 % | 0 % |
| `wtc_gasventil_ansteuersignal` | Gasventil-Ansteuersignal | `07/00/253F/00` | 2 | 0.01 % | 0 % |
| `wtc_gas_luft_verhaeltnis` | Gas-Luft-Verhältnis | `07/00/257D/00` | 2 | 0.01 % | 0 % |
| `wtc_ionisation_soll` | Ionisationssignal Sollwert | `07/00/2579/00` | 1 | 1 Pkt. | 3 Pkt. |
| `wtc_ionisation_start` | Ionisationssignal Start | `07/00/257A/00` | 1 | 1 Pkt. | 21 Pkt. |
| `wtc_ionisation_scot_ist` | Ionisationssignal SCOT-Istwert | `07/00/2539/00` | 1 | 1 Pkt. | 3 Pkt. |
| `wtc_ionisation_scot_basis` | Ionisationssignal SCOT-Basiswert | `07/00/253A/00` | 1 | 1 Pkt. | 90 Pkt. |

The internal pump reading is a controller target percentage, not electric power in watts or proof of physical rotation. These are sensors only; no combustion controls or writable targets are added. Other experimental registers are not promoted by this confirmation.

## Entity identity

The owner explicitly requested fresh regular entity IDs without EXP for these nine readings. Their internal keys change from `wtc_candidate_<suffix>` to `wtc_<suffix>`. Home Assistant creates new sensor entries on the boiler device using their normal names. Existing device names and user naming settings determine the exact resulting entity IDs.

The former nine extended EXP entities are no longer provided. Existing registry/history records are not automatically deleted. Other existing entities retain their keys and unique IDs. References and history are not automatically migrated to the new nine entries. A read-only check of this installation's YAML/JSON/JS/HTML configuration, stored Home Assistant dashboards/configuration and local cockpit source found no references to those nine former entity IDs or registry IDs before this change; external applications were not audited.

These changes are introduced in 0.5.1 and are not part of the 0.5.0 release. The historical evidence and limitations at that release remain in [field-validation-0.5.0.md](field-validation-0.5.0.md).
