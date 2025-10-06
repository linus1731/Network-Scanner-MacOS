from __future__ import annotations

import ipaddress
import os
import platform
import re
import socket
import subprocess
from typing import Optional, Tuple


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return out.stdout or ""
    except Exception:
        return ""


def _primary_ipv4_via_udp() -> Optional[str]:
    # Determine local IPv4 used for outbound traffic by opening a UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        # filter out loopback/bogus
        if not ip.startswith("127."):
            return ip
        return None
    except Exception:
        return None


def _macos_default_iface() -> Optional[str]:
    out = _run(["route", "-n", "get", "default"]) or _run(["route", "get", "default"]) 
    m = re.search(r"interface:\s*(\S+)", out)
    return m.group(1) if m else None


def _macos_iface_cidr(iface: str) -> Optional[str]:
    out = _run(["ifconfig", iface])
    # inet 192.168.1.5 netmask 0xffffff00 broadcast 192.168.1.255
    m = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+)\s+netmask\s+0x([0-9a-fA-F]+)", out)
    if not m:
        return None
    ip = m.group(1)
    mask_hex = int(m.group(2), 16)
    # Convert mask_hex to prefix length
    mask_bits = bin(mask_hex).count("1")
    try:
        ipaddress.ip_address(ip)
        return f"{ip}/{mask_bits}"
    except ValueError:
        return None


def _linux_iface_from_route() -> Tuple[Optional[str], Optional[str]]:
    out = _run(["ip", "route", "get", "8.8.8.8"]) 
    # Example: 8.8.8.8 via 192.168.1.1 dev wlan0 src 192.168.1.100 uid 1000
    dev = None
    src = None
    if out:
        mdev = re.search(r"\bdev\s+(\S+)", out)
        msrc = re.search(r"\bsrc\s+(\S+)", out)
        dev = mdev.group(1) if mdev else None
        src = msrc.group(1) if msrc else None
    return dev, src


def _linux_iface_cidr(iface: str) -> Optional[str]:
    out = _run(["ip", "-o", "-4", "addr", "show", "dev", iface])
    # Example: 3: wlan0    inet 192.168.1.100/24 brd 192.168.1.255 scope global dynamic noprefixroute wlan0\n
    m = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", out)
    if not m:
        return None
    ip = m.group(1)
    prefix = m.group(2)
    return f"{ip}/{prefix}"


def get_local_network_cidr() -> Optional[str]:
    system = platform.system().lower()
    if system == "darwin":
        iface = _macos_default_iface()
        if iface:
            cidr = _macos_iface_cidr(iface)
            if cidr:
                return cidr
        # fallback to /24 from primary IP
        ip = _primary_ipv4_via_udp()
        if ip:
            return f"{ip}/24"
        return None
    else:
        iface, src_ip = _linux_iface_from_route()
        if iface:
            cidr = _linux_iface_cidr(iface)
            if cidr:
                return cidr
        if src_ip:
            return f"{src_ip}/24"
        ip = _primary_ipv4_via_udp()
        if ip:
            return f"{ip}/24"
        return None


def get_primary_ipv4() -> Optional[str]:
    # Try command-derived src first (Linux path)
    if platform.system().lower() != "darwin":
        _, src = _linux_iface_from_route()
        if src:
            return src
    # Fallback via UDP trick
    return _primary_ipv4_via_udp()


def get_default_interface() -> Optional[str]:
    """Return the primary network interface used for default route, if detectable."""
    system = platform.system().lower()
    if system == "darwin":
        return _macos_default_iface()
    else:
        iface, _ = _linux_iface_from_route()
        return iface
