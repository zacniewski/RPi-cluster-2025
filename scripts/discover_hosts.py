#!/usr/bin/env python3
"""
Script to discover hostnames of devices in the local network.

This script scans the local network and attempts to retrieve the hostnames
of all connected devices using various methods including ARP scanning,
DNS resolution, and mDNS (multicast DNS) queries.

Usage:
    python3 discover_hosts.py [options]

Options:
    --interface INTERFACE  Specify network interface to use (default: auto-detect)
    --subnet SUBNET        Specify subnet to scan (default: auto-detect)
    --timeout TIMEOUT      Timeout for scan operations in seconds (default: 2)
    --verbose              Enable verbose output
    --help                 Show this help message and exit
"""

import argparse
import ipaddress
import os
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

try:
    import scapy.all as scapy
except ImportError:
    print("This script requires scapy. Install it with: pip install scapy")
    sys.exit(1)

try:
    import netifaces
except ImportError:
    print("This script requires netifaces. Install it with: pip install netifaces")
    sys.exit(1)

try:
    import zeroconf
except ImportError:
    print("Warning: zeroconf not installed. mDNS discovery will be limited.")
    print("Install it with: pip install zeroconf")
    HAS_ZEROCONF = False
else:
    HAS_ZEROCONF = True


def get_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Discover hostnames of devices in the local network")
    parser.add_argument("--interface", help="Network interface to use (default: auto-detect)")
    parser.add_argument("--subnet", help="Subnet to scan (default: auto-detect)")
    parser.add_argument("--timeout", type=float, default=2, help="Timeout for scan operations in seconds (default: 2)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def get_default_interface() -> str:
    """Get the default network interface."""
    try:
        # Get the default gateway interface
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET]
        return default_gateway[1]
    except (KeyError, IndexError):
        # Fallback: get the first non-loopback interface
        for interface in netifaces.interfaces():
            if interface != 'lo':
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    return interface

    # If all else fails, return loopback
    return 'lo'


def get_interface_ip(interface: str) -> str:
    """Get the IP address of the specified interface."""
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        return addresses[netifaces.AF_INET][0]['addr']
    return '127.0.0.1'  # Fallback to loopback


def get_subnet(interface: str) -> str:
    """Get the subnet for the specified interface."""
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        ip = addresses[netifaces.AF_INET][0]['addr']
        netmask = addresses[netifaces.AF_INET][0]['netmask']

        # Convert IP and netmask to CIDR notation
        ip_obj = ipaddress.IPv4Address(ip)
        netmask_obj = ipaddress.IPv4Address(netmask)

        # Count the number of 1's in the binary representation of the netmask
        netmask_binary = bin(int(netmask_obj))[2:]
        prefix_len = netmask_binary.count('1')

        # Return CIDR notation
        return f"{ip}/{prefix_len}"

    return '127.0.0.1/8'  # Fallback to loopback


def scan_network(subnet: str, timeout: float = 2) -> List[Dict[str, str]]:
    """
    Scan the network for active hosts using ARP requests.

    Args:
        subnet: Subnet to scan in CIDR notation (e.g., '192.168.1.0/24')
        timeout: Timeout for ARP responses in seconds

    Returns:
        List of dictionaries containing IP and MAC addresses of discovered devices
    """
    # Create ARP request packet
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request

    # Send packet and capture responses
    answered_list = scapy.srp(arp_request_broadcast, timeout=timeout, verbose=False)[0]

    # Process the responses
    devices = []
    for sent, received in answered_list:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices


def get_hostname_by_ip(ip: str) -> Optional[str]:
    """
    Try to resolve hostname from IP address using reverse DNS lookup.

    Args:
        ip: IP address to resolve

    Returns:
        Hostname if found, None otherwise
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return None


def get_hostname_by_mdns(ip: str) -> Optional[str]:
    """
    Try to resolve hostname using mDNS (multicast DNS).

    Args:
        ip: IP address to resolve

    Returns:
        Hostname if found, None otherwise
    """
    # Try to ping the .local domain to trigger mDNS resolution
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", f"{ip}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )

        # Check if there's a hostname in the output
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "PING" in line and ".local" in line:
                    parts = line.split()
                    for part in parts:
                        if ".local" in part:
                            return part.strip("()")
    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        pass

    return None


def resolve_hostname(ip: str) -> Tuple[str, Optional[str]]:
    """
    Resolve hostname for an IP address using multiple methods.

    Args:
        ip: IP address to resolve

    Returns:
        Tuple of (ip, hostname) where hostname may be None if not resolved
    """
    # Try standard DNS resolution first
    hostname = get_hostname_by_ip(ip)

    # If that fails, try mDNS
    if not hostname:
        hostname = get_hostname_by_mdns(ip)

    return ip, hostname


def check_root_privileges() -> bool:
    """Check if the script is running with root privileges."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # os.geteuid() is not available on Windows
        # For Windows, we'll assume the user has sufficient privileges
        return True


def main():
    """Main function to discover hosts in the local network."""
    args = get_arguments()

    # Determine the interface to use
    interface = args.interface or get_default_interface()
    if args.verbose:
        print(f"Using interface: {interface}")

    # Get the subnet to scan
    subnet = args.subnet or get_subnet(interface)
    if args.verbose:
        print(f"Scanning subnet: {subnet}")

    # Check for root privileges before scanning
    if not check_root_privileges():
        print("Error: This script requires root privileges to scan the network.")
        print("Please run the script with sudo: sudo ./discover_hosts.py")
        sys.exit(1)

    # Scan the network
    print("Scanning network for devices...")
    devices = scan_network(subnet, args.timeout)

    if not devices:
        print("No devices found. Try increasing the timeout or check your network connection.")
        return

    print(f"Found {len(devices)} devices on the network.")

    # Resolve hostnames in parallel
    print("Resolving hostnames...")
    with ThreadPoolExecutor(max_workers=min(32, len(devices))) as executor:
        ip_hostname_pairs = list(executor.map(
            lambda device: resolve_hostname(device['ip']), 
            devices
        ))

    # Create a mapping of IP to MAC
    ip_to_mac = {device['ip']: device['mac'] for device in devices}

    # Display results
    print("\nResults:")
    print("-" * 80)
    print(f"{'IP Address':<15} {'MAC Address':<18} {'Hostname':<40}")
    print("-" * 80)

    for ip, hostname in ip_hostname_pairs:
        mac = ip_to_mac.get(ip, "Unknown")
        hostname_display = hostname if hostname else "Unknown"
        print(f"{ip:<15} {mac:<18} {hostname_display:<40}")

    print("-" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
