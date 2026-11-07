# HK1 Heating Curve Slope

## Summary

Read-only Home Assistant sensor for heating curve slope
(Steilheit Heizkurve) of heating circuit 1.

## Confirmed CanApiJson address

| Field | Value |
|---|---|
| CM (read request) | 0x01 |
| MI | 0x02 |
| MX | 0x00 |
| OX | 0x254B |
| OS | 0x02 |
| VS | 2 bytes |
| Signed | No |
| Scale | 0.1 |

Read request:

`010200254b0200020000`

Example response:

`020200254b0200020055`

Raw value: 85

Decoded value: 8.5

## Home Assistant

Sensor definition key:

`sg_heizkurvensteilheit_hk1`

Display name:

`Heizkurvensteilheit HK1`

The sensor is read-only. No write operation is implemented.

## Validation

Tested on a Weishaupt WTC-GW 15-B installation
with WEM / CanApiJson access.

Observed values:

- Raw 85 = displayed slope 8.5
- Raw 90 = displayed slope 9.0

The register was repeatedly read successfully.
The reported value matched the heating curve slope
configured at the heating controller.

## Limitations

- Confirmed on one installation.
- Compatibility with other firmware versions
  and heating circuit configurations is not yet verified.
- No write support.
- Parallel shift is not implemented.

## Automated tests

The sensor regression tests verify:

- CAPI register addressing
- Two-byte unsigned value representation
- Scaling from raw values
- HK1 sensor group assignment
- Home Assistant sensor state conversion
