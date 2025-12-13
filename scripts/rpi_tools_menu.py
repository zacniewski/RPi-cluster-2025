#!/usr/bin/env python3
"""
RPi Helper Tools (Interactive Menu)

This Python script provides an interactive menu with 5 utility programs. Each option
runs a different Python routine useful on a Raspberry Pi or any Linux host.

Programs (menu options):

  1) Quick system overview
     - Shows hostname, OS version, CPU cores, load average, uptime, memory usage, and disk usage.

  2) Network connectivity check
     - Tests DNS resolution, TCP connectivity to common endpoints, and basic HTTP reachability.

  3) Find largest files
     - Scans a chosen directory (default: your HOME) and lists the largest files it can access.

  4) Start a simple HTTP server
     - Serves the current working directory over HTTP on a chosen port (default 8000).

  5) Generate a system report
     - Creates a timestamped text report under scripts/reports/ with system and network info.

Usage (how to run):
  - From the project root:
      python3 scripts/rpi_tools_menu.py
    or make it executable first:
      chmod +x scripts/rpi_tools_menu.py
      ./scripts/rpi_tools_menu.py

Notes:
  - Only standard library modules are used; no external dependencies are required.
  - Some information may require Linux-specific files like /proc; on other OSes, output may vary.
"""

from __future__ import annotations

import datetime as _dt
import os
import platform
import shutil
import socket
import sys
import textwrap
import time
import urllib.request
from pathlib import Path
from typing import List, Tuple


def _human_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(n)
    for u in units:
        if size < 1024.0:
            return f"{size:.2f} {u}"
        size /= 1024.0
    return f"{size:.2f} EB"


def _read_meminfo() -> Tuple[int, int, int]:
    """Return MemTotal, MemFree, MemAvailable in bytes if possible."""
    mem_total = mem_free = mem_available = 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1]) * 1024
                elif line.startswith("MemFree:"):
                    mem_free = int(line.split()[1]) * 1024
                elif line.startswith("MemAvailable:"):
                    mem_available = int(line.split()[1]) * 1024
    except Exception:
        pass
    return mem_total, mem_free, mem_available


def _uptime_seconds() -> float:
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except Exception:
        # Fallback best-effort
        return 0.0


def program_1_system_overview() -> None:
    print("\n=== System Overview ===")
    print(f"Hostname: {socket.gethostname()}")
    print(f"OS: {platform.platform()}")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    print(f"CPU cores (logical): {os.cpu_count()}")
    try:
        la1, la5, la15 = os.getloadavg()
        print(f"Load average (1/5/15m): {la1:.2f} {la5:.2f} {la15:.2f}")
    except (AttributeError, OSError):
        print("Load average: N/A on this platform")

    up = _uptime_seconds()
    if up:
        print(f"Uptime: {int(up)//3600}h {(int(up)%3600)//60}m {int(up)%60}s")
    else:
        print("Uptime: N/A")

    total, used, free = shutil.disk_usage("/")
    print("Root FS:")
    print(f"  Total: {_human_bytes(total)}  Used: {_human_bytes(used)}  Free: {_human_bytes(free)}")

    mt, mf, ma = _read_meminfo()
    if mt:
        used_mem = mt - ma if ma else mt - mf
        print("Memory:")
        print(f"  Total: {_human_bytes(mt)}  Used: {_human_bytes(used_mem)}  Free/Avail: {_human_bytes(ma or mf)}")
    else:
        print("Memory: N/A (no /proc/meminfo)")


def program_2_network_check() -> None:
    print("\n=== Network Connectivity Check ===")
    # DNS resolution
    for host in ["raspberrypi.org", "github.com", "google.com"]:
        try:
            ip = socket.gethostbyname(host)
            print(f"DNS: {host} -> {ip}")
        except Exception as e:
            print(f"DNS: {host} -> FAILED ({e})")

    # TCP connectivity
    tests = [
        ("8.8.8.8", 53, 2.0, "Google DNS:53"),
        ("1.1.1.1", 53, 2.0, "Cloudflare DNS:53"),
        ("github.com", 443, 3.0, "GitHub:443"),
    ]
    for host, port, timeout, label in tests:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                print(f"TCP: {label} -> OK")
        except Exception as e:
            print(f"TCP: {label} -> FAILED ({e})")

    # HTTP reachability
    try:
        with urllib.request.urlopen("http://example.com", timeout=4) as resp:
            print(f"HTTP: example.com -> {resp.status} {resp.reason}")
    except Exception as e:
        print(f"HTTP: example.com -> FAILED ({e})")


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Skip special or overly large virtual file systems
        if any(part in {"proc", "sys", "dev", ".git", "node_modules", "__pycache__"} for part in Path(dirpath).parts):
            continue
        for name in filenames:
            yield Path(dirpath) / name


def program_3_find_largest_files() -> None:
    print("\n=== Find Largest Files ===")
    default_dir = Path.home()
    choice = input(f"Directory to scan [default: {default_dir}]: ").strip()
    root = Path(choice or default_dir).expanduser().resolve()
    if not root.exists():
        print(f"Path does not exist: {root}")
        return
    try:
        limit = int(input("How many files to list? [default: 10]: ") or "10")
    except ValueError:
        limit = 10

    records: List[Tuple[int, Path]] = []
    scanned = 0
    start = time.time()
    for p in _iter_files(root):
        try:
            size = p.stat().st_size
            records.append((size, p))
            scanned += 1
        except Exception:
            continue
    records.sort(reverse=True, key=lambda t: t[0])
    took = time.time() - start
    print(f"Scanned {scanned} files under {root} in {took:.1f}s. Largest {limit}:")
    for i, (size, path) in enumerate(records[:limit], 1):
        print(f"{i:2d}. {_human_bytes(size):>10}  {path}")


def program_4_simple_http_server() -> None:
    import http.server
    import socketserver

    print("\n=== Simple HTTP Server ===")
    try:
        port = int(input("Port to use [default: 8000]: ") or "8000")
    except ValueError:
        port = 8000
    handler = http.server.SimpleHTTPRequestHandler
    addr = ("0.0.0.0", port)
    print(f"Serving directory: {Path.cwd()} on http://{addr[0]}:{addr[1]} (Ctrl+C to stop)")
    try:
        with socketserver.TCPServer(addr, handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


def program_5_generate_system_report() -> None:
    print("\n=== Generate System Report ===")
    project_root = Path(__file__).resolve().parents[1]
    reports_dir = project_root / "scripts" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = reports_dir / f"system-report-{ts}.txt"

    total, used, free = shutil.disk_usage("/")
    mt, mf, ma = _read_meminfo()
    try:
        la = os.getloadavg()
        la_str = f"{la[0]:.2f} {la[1]:.2f} {la[2]:.2f}"
    except Exception:
        la_str = "N/A"

    lines = [
        f"Timestamp: {_dt.datetime.now().isoformat()}",
        f"Hostname: {socket.gethostname()}",
        f"OS: {platform.platform()}",
        f"Python: {platform.python_version()} ({sys.executable})",
        f"CPU cores: {os.cpu_count()}",
        f"Load average: {la_str}",
        f"Uptime (s): {int(_uptime_seconds())}",
        "",
        "Disk /:",
        f"  Total: {_human_bytes(total)}",
        f"  Used:  {_human_bytes(used)}",
        f"  Free:  {_human_bytes(free)}",
        "",
        "Memory:",
        f"  Total: {_human_bytes(mt) if mt else 'N/A'}",
        f"  Avail: {_human_bytes(ma) if ma else 'N/A'}",
        f"  Free:  {_human_bytes(mf) if mf else 'N/A'}",
        "",
        "Network checks:",
        # We will perform quick checks similar to program 2
    ]

    # Append network checks
    for host in ["raspberrypi.org", "github.com", "google.com"]:
        try:
            ip = socket.gethostbyname(host)
            lines.append(f"  DNS {host}: {ip}")
        except Exception as e:
            lines.append(f"  DNS {host}: FAILED ({e})")

    for host, port, timeout, label in [
        ("8.8.8.8", 53, 2.0, "Google DNS:53"),
        ("1.1.1.1", 53, 2.0, "Cloudflare DNS:53"),
        ("github.com", 443, 3.0, "GitHub:443"),
    ]:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                lines.append(f"  TCP {label}: OK")
        except Exception as e:
            lines.append(f"  TCP {label}: FAILED ({e})")

    try:
        with urllib.request.urlopen("http://example.com", timeout=4) as resp:
            lines.append(f"  HTTP example.com: {resp.status} {resp.reason}")
    except Exception as e:
        lines.append(f"  HTTP example.com: FAILED ({e})")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written to: {report_path}")


def _print_menu() -> None:
    menu = textwrap.dedent(
        """
        ----------------------------------------
        RPi Cluster Helper Tools — Main Menu

        Choose an option:
          1) Quick system overview
          2) Network connectivity check
          3) Find largest files
          4) Start a simple HTTP server
          5) Generate a system report
          0) Exit
        ----------------------------------------
        """
    ).strip("\n")
    print(menu)


def main(argv: List[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv and argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0

    while True:
        _print_menu()
        choice = input("Enter choice [0-5]: ").strip()
        if choice == "1":
            program_1_system_overview()
        elif choice == "2":
            program_2_network_check()
        elif choice == "3":
            program_3_find_largest_files()
        elif choice == "4":
            program_4_simple_http_server()
        elif choice == "5":
            program_5_generate_system_report()
        elif choice == "0":
            print("Goodbye!")
            return 0
        else:
            print("Invalid choice. Please enter a number between 0 and 5.")

        # After running a program (except the long-running HTTP server), prompt to continue
        if choice != "4":
            _ = input("\nPress Enter to return to the menu, or Ctrl+C to exit...")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        raise SystemExit(130)
