# WTC 13 candidate sensors — cautious CanApiJson validation

This change exposes 13 read-only candidate entities on the WTC device, while
keeping all pre-existing device/HK1 entities and their identifiers untouched.

**Observed on a WTC-GW 15-B, 2026-11-10 (UTC):**

| Read address | Requested VS | Reply VS | Observed | Meaning (provisional) |
|---|---:|---:|---:|---|
| `07/00/2534/00` | 2 | 2 | `0x06A0` = 1696 | 16.96% burner output |
| `07/00/2540/00` | 2 | 2 | `0x03F8` = 1016 | 1016 rpm blower speed |
| `09/01/261B/02` | 2 | 1 | `0x0C` = 12 | 12 W internal pump power |

CAN documentation corroborates the proposed meaning. Independent comparison
against the WEM portal or device display remains desirable. The other ten
addresses/VS/scales are **candidate hypotheses**, NOT hardware-verified reads.
Source references:
- https://github.com/geronet1/wem-python
- https://github.com/jvejmelka/weishaupt-wem-can-esphome/blob/main/PROTOKOLL.md

## Polling behavior

The three one-shot responsive sensors use normal coordinator polling. The other
ten unverified candidate entities are `poll=False` in the normal loop and read
**one at a time**, using a separate one-register CanApiJson GET, at most once
per 180 seconds **total**. Thus each candidate is revisited every ~30 minutes
(assuming successful regular updates and no interruptions). They never send SET.

The slow polling loop disables itself until the next Home Assistant restart on
HTTP/communication failures or failed batches. A device CMD_ERROR is treated
as no supported data, not a numeric state. Returning a valid reply is necessary
but not sufficient to validate its interpretation, unit or scale. Do not claim
hardware validation for all 13 or merge them as production-stable without
further evidence. Keep both existing experimental catalog options disabled to
avoid duplicate probing.

### Known limitation

The burner output `07/00/2534/00` succeeded as a stand-alone GET, but was
`unavailable` when included in the integration's regular read batches. This
change does not claim to resolve the underlying intermittent/matching issue.
Investigate response VS/addresses and logs before advertising reliable live
burner output. The independent slow polling does not change this sensor.
