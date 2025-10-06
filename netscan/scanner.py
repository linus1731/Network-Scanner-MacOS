from __future__ import annotations

import ipaddress
import os
import platform
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Generator, List, Optional


@dataclass(frozen=True)
class PingResult:
    ip: str
    up: bool
    latency_ms: Optional[float]

    def as_dict(self) -> dict:
        return {"ip": self.ip, "up": self.up, "latency_ms": self.latency_ms}


def _build_ping_cmd(ip: str, count: int, timeout: float) -> List[str]:
    system = platform.system().lower()
    # macOS uses -W timeout in milliseconds; Linux uses -W timeout in seconds (for some ping variants)
    if system == "darwin":
        # macOS BSD ping: -c <count>, -W <ms> (per-packet timeout)
        ms = max(1, int(timeout * 1000))
        return ["/sbin/ping" if os.path.exists("/sbin/ping") else "ping", "-c", str(count), "-W", str(ms), ip]
    else:
        # Linux: prefer /bin/ping if present; -c <count>, -W <seconds> per-packet timeout
        sec = max(1, int(round(timeout)))
        return ["/bin/ping" if os.path.exists("/bin/ping") else "ping", "-c", str(count), "-W", str(sec), ip]


def ping(ip: str, count: int = 1, timeout: float = 1.0) -> PingResult:
    cmd = _build_ping_cmd(ip, count=count, timeout=timeout)
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=max(timeout * count + 0.5, timeout + 0.5),
            check=False,
        )
        output = proc.stdout or ""
        success = proc.returncode == 0 or ("bytes from" in output.lower())

        latency = None
        # Try to parse the first icmp reply time=XX ms
        m = re.search(r"time[=<]\\s*([0-9]+(?:\\.[0-9]+)?)\\s*ms", output, re.IGNORECASE)
        if m:
            latency = float(m.group(1))
        else:
            # Fallback to summary rtt line e.g., rtt min/avg/max/mdev = 0.032/0.032/0.032/0.000 ms
            m2 = re.search(r"=\\s*([0-9]+(?:\\.[0-9]+)?)/([0-9]+(?:\\.[0-9]+)?)/", output)
            if m2:
                latency = float(m2.group(2))

        return PingResult(ip=ip, up=bool(success), latency_ms=latency)
    except subprocess.TimeoutExpired:
        return PingResult(ip=ip, up=False, latency_ms=None)
    except Exception:
        # In case ping binary missing or other error
        return PingResult(ip=ip, up=False, latency_ms=None)


def expand_targets(target: str) -> List[str]:
    target = target.strip()
    # Range form: a.b.c.d-e or a.b.c.d-a.b.c.e
    if "-" in target and "/" not in target:
        start, end = target.split("-", 1)
        start_ip = ipaddress.ip_address(start)
        try:
            end_ip = ipaddress.ip_address(end)
        except ValueError:
            # If end is just the last octet
            base = start.split(".")
            if len(base) == 4 and end.isdigit():
                end_ip = ipaddress.ip_address(".".join(base[:3] + [end]))
            else:
                raise
        if int(end_ip) < int(start_ip):
            start_ip, end_ip = end_ip, start_ip
        return [str(ipaddress.ip_address(i)) for i in range(int(start_ip), int(end_ip) + 1)]

    # CIDR or single IP
    try:
        net = ipaddress.ip_network(target, strict=False)
        return [str(h) for h in net.hosts()] if net.num_addresses > 1 else [str(net.network_address)]
    except ValueError:
        # Single IP format may land here if not network
        ipaddress.ip_address(target)  # validate
        return [target]


def scan_cidr(target: str, concurrency: int = 128, timeout: float = 1.0, count: int = 1) -> Generator[dict, None, None]:
    hosts = expand_targets(target)
    if not hosts:
        return

    # Bound concurrency
    workers = max(1, min(concurrency, len(hosts), 1024))

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="netscan") as ex:
        future_map = {ex.submit(ping, ip, count=count, timeout=timeout): ip for ip in hosts}
        for fut in as_completed(future_map):
            res = fut.result()
            yield res.as_dict()
