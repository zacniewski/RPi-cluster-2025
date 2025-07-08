
<!-- USAGE EXAMPLES -->
## Usage

### Network Discovery Tool

The `discover_hosts.py` script allows discovering hostnames of devices in your local network. This is particularly useful when setting up a Raspberry Pi cluster to identify all the nodes.

#### Requirements

The script requires the following Python packages:
```sh
pip install scapy netifaces zeroconf
```

#### Running the Script

> **Note:** This script requires root privileges to perform network scanning operations. Always run it with `sudo`.

```sh
# Navigate to the scripts directory
cd scripts

# Run the script with default settings
sudo ./discover_hosts.py

# Run with verbose output
sudo ./discover_hosts.py --verbose

# Specify a network interface
sudo ./discover_hosts.py --interface eth0

# Specify a subnet to scan
sudo ./discover_hosts.py --subnet 192.168.1.0/24

# Increase timeout for slower networks
sudo ./discover_hosts.py --timeout 5
```

#### Example Output

```
Scanning network for devices...
Found 8 devices on the network.
Resolving hostnames...

Results:
--------------------------------------------------------------------------------
IP Address      MAC Address         Hostname                                
--------------------------------------------------------------------------------
192.168.18.1    f8:9b:6e:a0:3f:c0   router.local                            
192.168.18.10   d8:bb:c1:66:02:c8   desktop-pc.local                        
192.168.18.23   2c:cf:67:bf:e2:ec   pawn.local                              
192.168.18.24   e4:5f:01:8c:57:99   knight.local                            
192.168.18.25   e4:5f:01:8c:58:01   bishop.local                            
192.168.18.26   e4:5f:01:8c:59:32   rook.local                              
192.168.18.27   e4:5f:01:8c:60:45   queen.local                             
192.168.18.28   e4:5f:01:8c:61:78   king.local                              
--------------------------------------------------------------------------------
```

### Linux Commands for Network Hostname Discovery

If you prefer using standard Linux commands instead of the Python script, here are several commands that can help you discover hostnames of devices in your local network:

#### 1. Using nmap

[nmap](https://nmap.org/) is a powerful network scanning tool that can discover hosts and resolve their hostnames.

```sh
# Install nmap if not already installed
sudo apt install nmap

# Scan the local network and resolve hostnames
sudo nmap -sn 192.168.18.0/24 --dns-servers 192.168.18.1
```

#### 2. Using avahi-browse (for mDNS/Bonjour devices)

[Avahi](https://www.avahi.org/) is a system which facilitates service discovery on a local network.

```sh
# Install avahi-utils if not already installed
sudo apt install avahi-utils

# Browse for all services on the network
avahi-browse -a

# Browse for all hosts on the network
avahi-browse -at
```

#### 3. Using arp-scan

[arp-scan](https://github.com/royhills/arp-scan) is a tool that uses ARP packets to discover and fingerprint IP hosts on the local network.

```sh
# Install arp-scan if not already installed
sudo apt install arp-scan

# Scan the local network
sudo arp-scan --localnet

# Scan a specific interface
sudo arp-scan --interface=eth0 --localnet
```

#### 4. Using nbtscan (for Windows networks)

[nbtscan](http://www.unixwiz.net/tools/nbtscan.html) is a tool for scanning IP networks for NetBIOS name information.

```sh
# Install nbtscan if not already installed
sudo apt install nbtscan

# Scan the local network
sudo nbtscan 192.168.1.0/24
```

#### 5. Using a combination of ping and arp

This method uses standard Linux commands available on most distributions.

```sh
# Ping the broadcast address to populate the ARP table
ping -c 1 -b 192.168.1.255

# View the ARP table
arp -a
```

> **Note:** Replace `192.168.1.0/24` with your actual subnet in the examples above.

_For more examples, please refer to the [Documentation](https://example.com)_
