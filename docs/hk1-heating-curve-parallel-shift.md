# HK1 Heating Curve Parallel Shift

## Summary

Read-only Home Assistant sensor for the heating curve parallel shift
(Heizkurve Parallelverschiebung) of heating circuit 1.

## CanApiJson address

| Field | Value |
|---|---|
| Command (read) | `0x01` |
| Module index (MI) | `0x02` |
| Module extension (MX) | `0x00` |
| Object index (OX) | `0x25AD` |
| Object subindex (OS) | `0x02` |
| Value size (VS) | 2 bytes |
| Scale | 0.1 |
| Unit | K |
| Access | Read-only |

Example request:

`01020025ad0200020000`

Example response:

`02020025ad0200020055`

The raw value `85` represents `8.5 K`.

## Hardware validation

Validated on a Weishaupt WTC-GW 15-B installation using
the local CanApiJson interface.

Observed values:

| Controller setting | Raw value | Response payload |
|---|---|---|
| 8.5 K | 85 | `0055` |
| 8.0 K | 80 | `0050` |
| 8.5 K | 85 | `0055` |
| 9.0 K | 90 | `005a` |
| 8.5 K | 85 | `0055` |

The first three readings confirmed the A-B-A pattern.
Two later successful readings confirmed 9.0 K and 8.5 K.
One additional read failed because the HTTP response could
not be decoded as JSON; no incorrect value was observed.

The sensor was also observed updating in Home Assistant.

## Source of register hypothesis

The WEM CAN mapping in
https://github.com/geronet1/wem-python/blob/main/wem_codes.py
lists "Heizkurve Parallel" at CAN object `0x26AD`.
Comparison with confirmed CanApiJson addresses suggested
`0x25AD`, which was then verified on the hardware.

## Scope and limitations

- Read-only sensor; no write operation is implemented.
- Hardware validation is limited to one installation.
- Negative values are supported by the decoder but have not
  been confirmed against a negative controller setting.
- Compatibility with other models and firmware is unverified.
