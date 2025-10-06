from __future__ import annotations

import os
import re
from typing import Dict, Optional, Tuple


# Built-in tiny fallback to avoid showing nonsense when DB is missing
_OUI_FALLBACK: Dict[str, str] = {
    # A few common examples only; real coverage comes from external DBs
    "A45E60": "Apple, Inc.",
    "BC2411": "Apple, Inc.",
    "703EAC": "Apple, Inc.",
    "001A11": "Cisco Systems",
    "B827EB": "Raspberry Pi Foundation",
    "F0B479": "Samsung Electronics",
}


def _find_vendor_files() -> list[str]:
    # Common install locations for Wireshark and Nmap databases
    candidates = [
        # Wireshark manuf
        "/usr/share/wireshark/manuf",
        "/usr/local/share/wireshark/manuf",
        "/opt/homebrew/share/wireshark/manuf",  # macOS (ARM)
        # Nmap mac prefixes
        "/usr/share/nmap/nmap-mac-prefixes",
        "/usr/local/share/nmap/nmap-mac-prefixes",
        "/opt/homebrew/share/nmap/nmap-mac-prefixes",
    ]
    return [p for p in candidates if os.path.exists(p)]


def _parse_manuf_line(line: str) -> Optional[Tuple[str, int, str]]:
    # Wireshark format: "00:00:0C Cisco" or with prefix "AC:DE:48:00:00:00/36 SomeVendor"
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = re.split(r"\s+", line, maxsplit=2)
    if not parts:
        return None
    key = parts[0]
    name = parts[1] if len(parts) > 1 else ""
    if "/" in key:
        mac_part, plen = key.split("/", 1)
        try:
            plen = int(plen)
        except ValueError:
            return None
    else:
        mac_part, plen = key, 24  # default 24-bit OUI
    mac_hex = re.sub(r"[^0-9A-Fa-f]", "", mac_part).upper()
    if not mac_hex:
        return None
    # Store as hex string without separators, with prefix length in bits
    return mac_hex, int(plen), name


def _parse_nmap_line(line: str) -> Optional[Tuple[str, int, str]]:
    # Nmap format: "000000  XEROX CORPORATION"
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = re.match(r"^([0-9A-Fa-f]{6,12})\s+(.+)$", line)
    if not m:
        return None
    hexpart = m.group(1).upper()
    name = m.group(2).strip()
    plen = 4 * len(hexpart)  # 24 or 36 typically
    return hexpart, plen, name


def _load_oui_db() -> Dict[Tuple[int, str], str]:
    """Load OUI DB from Wireshark/Nmap if available.

    Returns a map keyed by (prefix_len_bits, hex_prefix) -> vendor.
    Longer prefixes should be preferred during lookup.
    """
    db: Dict[Tuple[int, str], str] = {}
    for path in _find_vendor_files():
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    rec = None
                    if path.endswith("manuf"):
                        rec = _parse_manuf_line(line)
                    else:
                        rec = _parse_nmap_line(line)
                    if not rec:
                        continue
                    hex_prefix, plen, name = rec
                    # Normalize prefix to exact nibble boundary
                    nibs = plen // 4
                    hex_prefix = hex_prefix[:nibs]
                    if nibs >= 6:  # at least 24-bit OUI
                        db[(plen, hex_prefix)] = name
        except Exception:
            continue
    # If nothing loaded, seed with fallback as 24-bit (6 hex digits)
    if not db:
        for hex6, name in _OUI_FALLBACK.items():
            db[(24, hex6)] = name
    return db


_DB = _load_oui_db()
_PREFERRED_PREFIXES = sorted({plen for (plen, _k) in _DB.keys()}, reverse=True)  # e.g., [36, 24]


def _is_locally_administered(hex12: str) -> bool:
    """Detect Locally Administered Address (randomized MAC), based on first octet bit 1."""
    if len(hex12) < 2:
        return False
    try:
        first_octet = int(hex12[:2], 16)
    except ValueError:
        return False
    return bool(first_octet & 0x02)


def vendor_from_mac(mac: str) -> Optional[str]:
    if not mac:
        return None
    hex_only = "".join(c for c in mac if c.isalnum()).upper()
    if len(hex_only) < 12:
        # Not a full MAC, try best-effort on available prefix
        if len(hex_only) >= 6:
            for plen in _PREFERRED_PREFIXES:
                nibs = plen // 4
                if len(hex_only) >= nibs:
                    name = _DB.get((plen, hex_only[:nibs]))
                    if name:
                        return name
        return None

    # If locally administered (randomized), OUI mapping is meaningless
    if _is_locally_administered(hex_only):
        return "Locally administered (randomized)"

    # Longest-prefix match (prefer 36-bit if present, then 24-bit)
    for plen in _PREFERRED_PREFIXES:
        nibs = plen // 4
        if len(hex_only) >= nibs:
            name = _DB.get((plen, hex_only[:nibs]))
            if name:
                return name
    return None
