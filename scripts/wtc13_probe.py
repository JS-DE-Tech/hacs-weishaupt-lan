#!/usr/bin/env python3
"""One-shot, strictly read-only CanApiJson validation of 13 candidate WTC registers.

For an operator's local WEM SG only. No SET command exists in this script.
No dependencies beyond Python 3.10+ are required.
"""
from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CMD_GET = 0x01
CMD_RESPONSE = 0x02
CMD_ERROR = 0x05

@dataclass(frozen=True)
class Candidate:
    key: str
    mi: int
    mx: int
    ox: int
    os: int
    request_vs: int
    response_vs: int
    hint: str

# The candidate addresses and response sizes match PR #14 as of 2026-11-10.
# Units/semantic labels are provisional, even when a numeric answer is received.
CANDIDATES: tuple[Candidate, ...] = (
    Candidate("wtc_brenner_istleistung_kandidat", 0x07,0x00,0x2534,0x00,2,2,"Burner current output, possibly 0.01%"),
    Candidate("wtc_geblaesedrehzahl_kandidat", 0x07,0x00,0x2540,0x00,2,2,"Blower speed, possibly rpm"),
    Candidate("wtc_pumpe_intern_elektrische_leistung_kandidat", 0x09,0x01,0x261B,0x02,2,1,"Internal electric pump power, possibly W"),
    Candidate("wtc_kessel_vorlauf_ist_kandidat", 0x07,0x00,0x2536,0x00,2,2,"Boiler flow temperature, possibly 0.1°C"),
    Candidate("wtc_brenner_sollleistung_kandidat", 0x07,0x00,0x2542,0x00,2,2,"Burner target output (scale unverified)"),
    Candidate("wtc_geblaese_ansteuerung_kandidat", 0x07,0x00,0x257E,0x00,2,2,"Blower control (scale unverified)"),
    Candidate("wtc_brennertaktsperre_kandidat", 0x07,0x00,0x250A,0x00,1,1,"Burner anti-cycling time (units unverified)"),
    Candidate("wtc_schaltdifferenz_heizbetrieb_kandidat", 0x07,0x00,0x250D,0x02,2,2,"Heating differential, possibly 0.1K"),
    Candidate("wtc_brennerleistung_max_heizbetrieb_kandidat", 0x07,0x00,0x2523,0x02,2,2,"Max heating burner output, possibly 0.01%"),
    Candidate("wtc_pumpenleistung_min_heizbetrieb_kandidat", 0x07,0x00,0x256B,0x02,1,1,"Minimum heating pump percent (unverified)"),
    Candidate("wtc_pumpenleistung_max_heizbetrieb_kandidat", 0x07,0x00,0x256C,0x02,1,1,"Maximum heating pump percent (unverified)"),
    Candidate("wtc_pumpenregelungsart_kandidat", 0x09,0x01,0x266A,0x02,1,1,"Pump regulation mode (unverified)"),
    Candidate("wtc_vpt_max_volumenstrom_kandidat", 0x09,0x01,0x2629,0x02,2,2,"Maximum VPT flow, possibly l/h"),
)


def build_vg(c: Candidate) -> str:
    """Construct precisely one CMD_GET; request size can differ from reply size."""
    return (f"{CMD_GET:02x}{c.mi:02x}{c.mx:02x}{c.ox:04x}"
            f"{c.os:02x}{c.request_vs:04x}" + "00" * c.request_vs)


def read_payload(c: Candidate) -> dict[str, Any]:
    return {"ID": "12345678", "SRC": "DDC", "CAPI": {"NN": 1, "N01": {"VG": build_vg(c)}}}


def parse_reply(payload: dict[str, Any], candidate: Candidate) -> dict[str, Any]:
    """Strictly match command, address, response size and value payload."""
    capi = payload.get("CAPI")
    if not isinstance(capi, dict):
        return {"status": "no_capi"}
    frame = capi.get("N01")
    if not isinstance(frame, dict) or not isinstance(frame.get("VG"), str):
        return {"status": "no_frame"}
    vg = frame["VG"].strip()
    try:
        if len(vg) < 16 or len(vg) % 2:
            raise ValueError("Invalid VG length")
        cmd = int(vg[0:2], 16)
        mi = int(vg[2:4], 16)
        mx = int(vg[4:6], 16)
        ox = int(vg[6:10], 16)
        os_val = int(vg[10:12], 16)
        vs = int(vg[12:16], 16)
        value_hex = vg[16:]
        bytes.fromhex(value_hex)
    except ValueError:
        return {"status": "invalid_vg", "vg": vg}
    if (mi, mx, ox, os_val) != (candidate.mi, candidate.mx, candidate.ox, candidate.os):
        return {"status": "wrong_address", "vg": vg}
    if cmd == CMD_ERROR:
        return {"status": "unsupported_or_error", "vg": vg}
    if cmd != CMD_RESPONSE:
        return {"status": "unexpected_command", "command": cmd, "vg": vg}
    if vs != candidate.response_vs or len(value_hex) != vs * 2:
        return {"status": "wrong_response_size", "response_vs": vs, "vg": vg}
    raw = int(value_hex, 16)
    if (vs == 2 and raw in (0x8000, 0xFFFF)) or (vs == 4 and raw in (0x80000000, 0xFFFFFFFF)):
        return {"status": "sentinel_unavailable", "raw_hex": value_hex.upper(),
                "response_vs": vs, "vg": vg}
    return {"status": "response", "raw_unsigned": raw,
            "raw_hex": value_hex.upper(), "response_vs": vs, "vg": vg}


def request_one(host: str, username: str, password: str, candidate: Candidate,
                timeout: float = 15.0) -> dict[str, Any]:
    body = json.dumps(read_payload(candidate), separators=(",", ":")).encode("utf-8")
    authorization = base64.b64encode(f"{username}:{password}".encode()).decode()
    req = Request(f"http://{host}/ajax/CanApiJson.json", data=body, method="POST",
                  headers={"Authorization": f"Basic {authorization}",
                           "Content-Type": "application/json", "Accept": "application/json",
                           "Referer": f"http://{host}/", "Connection": "close"})
    try:
        with urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read(1024 * 1024).decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        # Do not return header values or credentials in logs.
        error = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
        return {"status": "transport_error", "error": error}
    if not isinstance(data, dict):
        return {"status": "invalid_json"}
    return parse_reply(data, candidate)


def probe(host: str, username: str, password: str, pause: float,
          timeout: float, dry_run: bool) -> list[dict[str, Any]]:
    rows = []
    for index, candidate in enumerate(CANDIDATES, start=1):
        if index > 1 and not dry_run:
            time.sleep(pause)
        result = ({"status": "dry_run", "request_vg": build_vg(candidate)} if dry_run
                  else request_one(host, username, password, candidate, timeout))
        row = {"number": index, "key": candidate.key, "mi": f"{candidate.mi:02X}",
               "mx": f"{candidate.mx:02X}", "ox": f"{candidate.ox:04X}",
               "os": f"{candidate.os:02X}", "request_vs": candidate.request_vs,
               "expected_response_vs": candidate.response_vs, "hint": candidate.hint,
               **result}
        rows.append(row)
        raw = f"raw={row['raw_unsigned']}" if "raw_unsigned" in row else ""
        print(f"[{index:02}/13] {candidate.key}: {result['status']} {raw}", flush=True)
        # Stop on connection/authentication failures rather than hammering an unhealthy WEM.
        if result["status"] == "transport_error":
            print("Communication error: stopping further probes for device safety.", file=sys.stderr)
            break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Read 13 WTC candidate registers once (GET only)")
    parser.add_argument("--host", default=os.getenv("WEM_HOST", ""), help="LAN host/IP of WEM system device")
    parser.add_argument("--username", default=os.getenv("WEM_USER", "admin"))
    parser.add_argument("--pause", type=float, default=3.0, help="Seconds between reads; minimum 3.0")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", type=Path, default=Path("wtc13_probe_results.json"))
    parser.add_argument("--dry-run", action="store_true", help="Show GET frames without contacting WEM")
    args = parser.parse_args()
    if not args.dry_run and not args.host:
        parser.error("--host or WEM_HOST is required for actual polling")
    if args.pause < 3:
        parser.error("--pause must be at least 3 seconds")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.host and ("/" in args.host or "://" in args.host or "@" in args.host):
        parser.error("--host must be a hostname/IP only, without scheme or path")
    password = "" if args.dry_run else (os.getenv("WEM_PASSWORD") or getpass.getpass("WEM password (not stored): "))
    rows = probe(args.host, args.username, password, args.pause, args.timeout, args.dry_run)
    result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "dry_run": args.dry_run, "total_expected": len(CANDIDATES),
              "queried": len(rows), "responses": sum(r["status"] == "response" for r in rows),
              "note": "Candidate meaning and scale require manual validation against controller display",
              "results": rows}
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output} — {result['responses']}/{len(rows)} strict numeric replies")
    return 1 if len(rows) < len(CANDIDATES) else 0


if __name__ == "__main__":
    raise SystemExit(main())
