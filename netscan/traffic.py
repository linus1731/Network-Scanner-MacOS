from __future__ import annotations

import platform
import re
import subprocess
from typing import Optional, Tuple


def _run(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        return p.stdout or ""
    except Exception:
        return ""


def get_bytes_counters(interface: str) -> Optional[Tuple[int, int]]:
    """Return (rx_bytes, tx_bytes) for the given interface, or None if not found."""
    system = platform.system().lower()
    if system == "darwin":
        out = _run(["netstat", "-ibn"])  # columns include Ibytes Obytes
        # Name  Mtu   Network     Address            Ibytes     Obytes ...
        rx = tx = None
        for line in out.splitlines():
            parts = line.split()
            if not parts or parts[0] != interface:
                continue
            # Try to locate Ibytes/OBytes assuming typical column order
            # Some versions have: Name Mtu Net ... Ipkts Ierrs Opkts Oerrs Coll Ibytes Obytes ...
            m = re.findall(r"\s(\d+)\s(\d+)\s*$", line)
            # Fallback: parse by column headers position
            if "Ibytes" in out and "Obytes" in out:
                # attempt header index mapping
                header = None
                for hl in out.splitlines():
                    if hl.strip().startswith("Name") and "Ibytes" in hl and "Obytes" in hl:
                        header = hl
                        break
                if header:
                    hcols = header.split()
                    cols = line.split()
                    try:
                        i_idx = hcols.index("Ibytes")
                        o_idx = hcols.index("Obytes")
                        rx = int(cols[i_idx])
                        tx = int(cols[o_idx])
                        return rx, tx
                    except Exception:
                        pass
            # Very rough fallback: not reliable
        return None
    else:
        # Linux: /proc/net/dev
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    if_name, rest = [s.strip() for s in line.split(":", 1)]
                    if if_name != interface:
                        continue
                    fields = rest.split()
                    # fields: recv: bytes packets errs drop fifo frame compressed multicast
                    #          trans: bytes packets errs drop fifo colls carrier compressed
                    if len(fields) >= 16:
                        rx = int(fields[0])
                        tx = int(fields[8])
                        return rx, tx
        except Exception:
            return None
        return None
