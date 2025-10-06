from __future__ import annotations

import argparse
import json
import sys
from typing import List
import ipaddress

from .scanner import scan_cidr
from .netinfo import get_local_network_cidr, get_primary_ipv4
from .colors import supports_color, paint, Color
from .resolve import resolve_ptrs
from .arp import get_arp_table
from .export import export_to_csv, export_to_markdown, export_to_html
from .ratelimit import get_global_limiter
from .profiles import (
    get_profile,
    list_profiles,
    save_custom_profile,
    ScanProfile,
    PREDEFINED_PROFILES
)


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
        "-p",
        "--profile",
        type=str,
        metavar="NAME",
        help="Use a scan profile (quick, normal, thorough, stealth, or custom)",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available scan profiles and exit",
    )
    parser.add_argument(
        "--save-profile",
        type=str,
        metavar="NAME",
        help="Save current settings as a custom profile",
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
        "--rate-limit",
        type=float,
        metavar="N",
        help="Limit scan rate to N requests per second (default: no limit)",
    )
    parser.add_argument(
        "--burst",
        type=int,
        metavar="N",
        help="Maximum burst size for rate limiting (default: rate * 2)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        metavar="FILE",
        help="Export results to CSV file",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        metavar="FILE",
        help="Export results to Markdown file",
    )
    parser.add_argument(
        "--output-html",
        type=str,
        metavar="FILE",
        help="Export results to HTML file (interactive report)",
    )
    parser.add_argument(
        "--include-down",
        action="store_true",
        help="Include DOWN hosts in export (default: only UP hosts)",
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emoji in Markdown export (use UP/DOWN text)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info (why hostname/MAC is missing)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv if argv is not None else sys.argv[1:])
    
    # Configure rate limiting if specified
    if ns.rate_limit is not None:
        limiter = get_global_limiter()
        burst = ns.burst if ns.burst is not None else int(ns.rate_limit * 2)
        limiter.set_rate(ns.rate_limit, burst)
        
        color_on = supports_color() and not ns.no_color
        print(paint(f"⚙️  Rate limiting: {ns.rate_limit} req/s (burst: {burst})", 
                   Color.CYAN, enable=color_on))
    
    # Handle --list-profiles
    if ns.list_profiles:
        color_on = supports_color() and not ns.no_color
        print(paint("Available Scan Profiles:", Color.BOLD, enable=color_on))
        print()
        
        profiles = list_profiles()
        
        # Show predefined profiles first
        print(paint("Predefined Profiles:", Color.CYAN, Color.BOLD, enable=color_on))
        for name in ['quick', 'normal', 'thorough', 'stealth']:
            if name in profiles:
                profile = profiles[name]
                print(f"  {paint(name, Color.GREEN, Color.BOLD, enable=color_on):<20} - {profile.description}")
                print(f"    Concurrency: {profile.concurrency}, Timeout: {profile.timeout}s, Ports: {profile.port_range}")
                if profile.rate_limit:
                    print(f"    Rate Limit: {profile.rate_limit} pkts/s")
                if profile.random_delay:
                    print(f"    Random Delay: {profile.min_delay}-{profile.max_delay}s")
                print()
        
        # Show custom profiles
        custom_profiles = {k: v for k, v in profiles.items() if k not in PREDEFINED_PROFILES}
        if custom_profiles:
            print(paint("Custom Profiles:", Color.MAGENTA, Color.BOLD, enable=color_on))
            for name, profile in custom_profiles.items():
                print(f"  {paint(name, Color.YELLOW, Color.BOLD, enable=color_on):<20} - {profile.description}")
                print(f"    Concurrency: {profile.concurrency}, Timeout: {profile.timeout}s, Ports: {profile.port_range}")
                print()
        
        return 0
    
    # Apply profile settings
    active_profile = None
    if ns.profile:
        active_profile = get_profile(ns.profile)
        if not active_profile:
            print(paint(f"❌ Profile '{ns.profile}' not found. Use --list-profiles to see available profiles.", 
                       Color.RED, Color.BOLD, enable=supports_color()), file=sys.stderr)
            return 1
        
        # Apply profile settings (can be overridden by CLI args)
        if not any([hasattr(ns, 'concurrency') and ns.concurrency != 128]):  # Check if default
            ns.concurrency = active_profile.concurrency
        if not any([hasattr(ns, 'timeout') and ns.timeout != 1.0]):  # Check if default
            ns.timeout = active_profile.timeout
        # Note: port_range will be handled in TUI/scanner integration
    
    # Handle --save-profile
    if ns.save_profile:
        new_profile = ScanProfile(
            name=ns.save_profile,
            description=f"Custom profile '{ns.save_profile}'",
            concurrency=ns.concurrency,
            timeout=ns.timeout,
            port_range='top1000',  # Default
        )
        
        if save_custom_profile(new_profile):
            color_on = supports_color() and not ns.no_color
            print(paint(f"✅ Profile '{ns.save_profile}' saved successfully!", Color.GREEN, Color.BOLD, enable=color_on))
        else:
            print(paint(f"❌ Failed to save profile '{ns.save_profile}'", Color.RED, Color.BOLD, enable=color_on), file=sys.stderr)
            return 1

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
    
    # Show active profile message
    if active_profile:
        color_on = supports_color() and not ns.no_color
        profile_msg = f"Using profile: {paint(active_profile.name, Color.CYAN, Color.BOLD, enable=color_on)} - {active_profile.description}"
        print(profile_msg)

    results = list(
        scan_cidr(
            target,
            concurrency=ns.concurrency,
            timeout=ns.timeout,
            count=ns.count,
        )
    )

    # Enrich with PTR hostnames and ARP MAC (best-effort; do not block long)
    ips = [r["ip"] for r in results]
    ptr = resolve_ptrs(ips)
    arp_map = get_arp_table()
    for r in results:
        r["hostname"] = ptr.get(r["ip"]) or None
        r["mac"] = arp_map.get(r["ip"]) or None

    # Export to CSV if requested
    if ns.output_csv:
        try:
            output_path = export_to_csv(results, ns.output_csv, include_down=ns.include_down)
            color_on = supports_color() and not ns.no_color
            print(paint(f"✅ CSV exported to: {output_path}", Color.GREEN, Color.BOLD, enable=color_on))
        except Exception as e:
            print(paint(f"❌ CSV export failed: {e}", Color.RED, Color.BOLD, enable=color_on), file=sys.stderr)
            return 1

    # Export to Markdown if requested
    if ns.output_md:
        try:
            use_emoji = not ns.no_emoji
            output_path = export_to_markdown(results, ns.output_md, include_down=ns.include_down, use_emoji=use_emoji)
            color_on = supports_color() and not ns.no_color
            print(paint(f"✅ Markdown exported to: {output_path}", Color.GREEN, Color.BOLD, enable=color_on))
        except Exception as e:
            print(paint(f"❌ Markdown export failed: {e}", Color.RED, Color.BOLD, enable=color_on), file=sys.stderr)
            return 1
    
    # Export to HTML if requested
    if ns.output_html:
        try:
            output_path = export_to_html(results, ns.output_html, include_down=ns.include_down)
            color_on = supports_color() and not ns.no_color
            print(paint(f"✅ HTML exported to: {output_path}", Color.GREEN, Color.BOLD, enable=color_on))
        except Exception as e:
            print(paint(f"❌ HTML export failed: {e}", Color.RED, Color.BOLD, enable=color_on), file=sys.stderr)
            return 1

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
        print(paint(f"{'IP Address':<16}  {'Status':<6}  {'Latency':>9}  {'Hostname':<32}  {'MAC':<17}", Color.BOLD, enable=color_on))
        print(paint("-" * 16 + "  " + "-" * 6 + "  " + "-" * 9 + "  " + "-" * 32 + "  " + "-" * 17, Color.DIM, enable=color_on))

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
            host_s = (r.get("hostname") or "-")[:32]
            mac_s = r.get("mac") or "-"
            print(f"{ip_s}  {status:<6}  {lat_s:>9}  {host_s:<32}  {mac_s:<17}")

        if ns.debug:
            print()
            print(paint("Debug (Hostname/MAC):", Color.YELLOW, Color.BOLD, enable=color_on))
            for r in results:
                reasons = []
                if not r.get("hostname"):
                    reasons.append("no PTR/mDNS")
                if not r.get("mac"):
                    reasons.append("no ARP entry")
                if not reasons:
                    reasons.append("ok")
                print(f"  {r['ip']}: " + ", ".join(reasons))

    # Exit non-zero if nothing was reachable
    return 0 if any(r["up"] for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
