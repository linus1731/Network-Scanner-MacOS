from __future__ import annotations

import platform
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, Optional, List
import subprocess
import re


def _ptr(ip: str) -> Optional[str]:
    try:
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return None


def resolve_ptrs(ips: Iterable[str], concurrency: int = 32, timeout_per_lookup: float = 0.5) -> Dict[str, Optional[str]]:
    ips = list(dict.fromkeys(ips))  # de-dup preserve order
    res: Dict[str, Optional[str]] = {ip: None for ip in ips}
    if not ips:
        return res
    workers = max(1, min(concurrency, len(ips), 128))
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netscan-dns") as ex:
        futures = {ex.submit(_ptr, ip): ip for ip in ips}
        for fut in as_completed(futures, timeout=None):
            ip = futures[fut]
            try:
                res[ip] = fut.result(timeout=timeout_per_lookup)
            except Exception:
                res[ip] = None

    # Best-effort fallbacks for unresolved IPs
    unresolved = [ip for ip, name in res.items() if name is None]
    if unresolved:
        # 1) Linux: avahi-resolve-address (mDNS)
        try:
            p = subprocess.run(["avahi-resolve-address"] + unresolved, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=1.5)
            out = p.stdout or ""
            for line in out.splitlines():
                parts = re.split(r"\s+", line.strip())
                if len(parts) >= 2:
                    ip, host = parts[0], parts[1]
                    if ip in res and res[ip] is None:
                        res[ip] = host
        except Exception:
            pass

        # 2) macOS: dns-sd reverse PTR query per IP
        if platform.system().lower() == "darwin":
            def _rev_arpa(ip: str) -> str:
                parts = ip.split(".")
                if len(parts) == 4:
                    return f"{parts[3]}.{parts[2]}.{parts[1]}.{parts[0]}.in-addr.arpa"
                return ip
            for ip in list(unresolved):
                if res.get(ip):
                    continue
                try:
                    qname = _rev_arpa(ip)
                    p = subprocess.run(["dns-sd", "-Q", qname, "PTR"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=1.5)
                    out = p.stdout or ""
                    # Look for lines that contain the queried name and a hostname ending with a dot
                    # Example snippet often includes: "Add     2   4   <qname>.   PTR   <hostname>."
                    m = re.search(r"PTR\s+([A-Za-z0-9_.-]+)\.?\s*$", out, re.MULTILINE)
                    if m:
                        host = m.group(1).rstrip('.')
                        if host and res.get(ip) is None:
                            res[ip] = host
                except Exception:
                    pass

        # 3) Generic: host or dig reverse lookup
        still = [ip for ip in unresolved if res.get(ip) is None]
        if still:
            # Try `host -W 1 <ip>` (if available)
            for ip in list(still):
                try:
                    p = subprocess.run(["host", "-W", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=1.5)
                    out = (p.stdout or "").strip()
                    m = re.search(r"pointer\s+([^\s]+)\.?$", out, re.IGNORECASE)
                    if m:
                        name = m.group(1).rstrip('.')
                        if name:
                            res[ip] = name
                            continue
                except Exception:
                    pass
            # Try `dig -x <ip> +short +time=1`
            still2 = [ip for ip in still if res.get(ip) is None]
            for ip in list(still2):
                try:
                    p = subprocess.run(["dig", "-x", ip, "+short", "+time=1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False, timeout=1.5)
                    out = (p.stdout or "").strip()
                    cand = next((ln.strip().rstrip('.') for ln in out.splitlines() if ln.strip()), None)
                    if cand:
                        res[ip] = cand
                except Exception:
                    pass
    return res
