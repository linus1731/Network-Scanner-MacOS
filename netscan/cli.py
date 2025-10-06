from __future__ import annotations

import argparse
import json
import sys
from typing import List
import ipaddress

from .scanner import scan_cidr
from .netinfo import get_local_network_cidr, get_primary_ipv4
from .colors import supports_color, paint, Color


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="netscan",
        description="Concurrent ping sweep for macOS and Linux with latency reporting.",
    )
    parser.add_argument(
        "cidr",
        nargs="?",
        help="CIDR or IP range to scan (optional). Wenn leer, wird das lokale Netz automatisch ermittelt.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=128,
        help="Number of concurrent pings (default: 128)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=1.0,
        help="Per-host timeout in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Echo requests per host (default: 1)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv if argv is not None else sys.argv[1:])

    target = ns.cidr
    auto_msg = None
    if not target:
        cidr = get_local_network_cidr()
        if not cidr:
            print("Konnte lokales Netz nicht automatisch ermitteln. Bitte CIDR/Range/IP angeben.", file=sys.stderr)
            return 1
        target = cidr
        ip = get_primary_ipv4() or "?"
        auto_msg = f"Automatisch erkannt: {target} (lokale IP: {ip})"

    results = list(
        scan_cidr(
            target,
            concurrency=ns.concurrency,
            timeout=ns.timeout,
            count=ns.count,
        )
    )

    if ns.json:
        print(json.dumps(results, indent=2))
    else:
        color_on = supports_color() and not ns.no_color
        up = [r for r in results if r["up"]]
        down = [r for r in results if not r["up"]]

        header = f"Scanned {len(results)} hosts: "
        header += paint(f"{len(up)} up", Color.GREEN, Color.BOLD, enable=color_on)
        header += ", "
        header += paint(f"{len(down)} down", Color.RED, Color.BOLD, enable=color_on)
        print(header)

        if auto_msg:
            print(paint(auto_msg, Color.DIM, enable=color_on))

        # Table header
        print()
        print(paint(f"{'IP Address':<16}  {'Status':<6}  {'Latency':>9}", Color.BOLD, enable=color_on))
        print(paint("-" * 16 + "  " + "-" * 6 + "  " + "-" * 9, Color.DIM, enable=color_on))

        def ip_sort_key(ip: str):
            try:
                return int(ipaddress.ip_address(ip))
            except Exception:
                return 0

        for r in sorted(results, key=lambda x: ip_sort_key(x["ip"])):
            status = paint("UP", Color.GREEN, Color.BOLD, enable=color_on) if r["up"] else paint("DOWN", Color.RED, Color.BOLD, enable=color_on)
            if r["latency_ms"] is None:
                lat_s = paint("-", Color.DIM, enable=color_on)
            else:
                ms = r["latency_ms"]
                if ms < 20:
                    style = Color.GREEN
                elif ms < 100:
                    style = Color.YELLOW
                else:
                    style = Color.MAGENTA
                lat_s = paint(f"{ms:.2f} ms", style, enable=color_on)
            ip_s = paint(f"{r['ip']:<16}", Color.CYAN, enable=color_on)
            print(f"{ip_s}  {status:<6}  {lat_s:>9}")

    # Exit non-zero if nothing was reachable
    return 0 if any(r["up"] for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
