from __future__ import annotations

import platform
import re
import subprocess
from typing import Dict, Optional


def _run(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        return p.stdout or ""
    except Exception:
        return ""


def get_arp_table() -> Dict[str, str]:
    """Return a best-effort IP->MAC mapping for the local network.

    Works on macOS (arp -an) and Linux (ip neigh / arp -an).
    """
    system = platform.system().lower()
    out = ""
    if system == "darwin":
        out = _run(["arp", "-an"])  # (ip) at (mac) on ifscope
        # Example: ? (192.168.1.1) at a4:xx:xx:xx:xx:xx on en0 ifscope [ethernet]
        pattern = re.compile(r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-f:]{11,})", re.IGNORECASE)
    else:
        out = _run(["ip", "neigh"]) or _run(["arp", "-an"])  # fallback
        # ip neigh: 192.168.1.1 dev wlan0 lladdr a4:xx:xx:xx:xx:xx REACHABLE
        pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+.*?lladdr\s+([0-9a-f:]{11,})", re.IGNORECASE)
        if not pattern.search(out):
            # fallback parse for arp -an
            pattern = re.compile(r"\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-f:]{11,})", re.IGNORECASE)

    mapping: Dict[str, str] = {}
    for ip, mac in pattern.findall(out):
        mac = mac.lower()
        mapping[ip] = mac
    return mapping
