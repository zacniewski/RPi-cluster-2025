## Software installation for RPi cluster  

1. RPi Imager  
- link to [official page](https://www.raspberrypi.com/software/),  
- link to [GitHub](https://github.com/raspberrypi/rpi-imager).  

obrazki z instalacji OS

Interfejsy sieciowe
On one machine (laptop + WiFi)
```bash
$ ifconfig
enp3s0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether d4:93:90:2a:5e:68  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 5805  bytes 562751 (562.7 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5805  bytes 562751 (562.7 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlp0s20f3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.18.13  netmask 255.255.255.0  broadcast 192.168.18.255
        inet6 fe80::ba1c:c7e2:3761:bbeb  prefixlen 64  scopeid 0x20<link>
        ether dc:46:28:8b:14:c9  txqueuelen 1000  (Ethernet)
        RX packets 1171156  bytes 1637420945 (1.6 GB)
        RX errors 0  dropped 251  overruns 0  frame 0
        TX packets 234914  bytes 31826155 (31.8 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

On the second machine (PC connected to switch)
```bash
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether c2:66:6f:37:b6:93  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

enp34s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.18.17  netmask 255.255.255.0  broadcast 192.168.18.255
        inet6 fe80::914a:7757:29e5:997  prefixlen 64  scopeid 0x20<link>
        ether 00:d8:61:54:64:82  txqueuelen 1000  (Ethernet)
        RX packets 173771  bytes 199545810 (199.5 MB)
        RX errors 0  dropped 212  overruns 0  frame 0
        TX packets 76599  bytes 17450476 (17.4 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 3584  bytes 39513593 (39.5 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 3584  bytes 39513593 (39.5 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

The private addresses start with `192.168.18.XX` in my home network.  
Yours could be different.


ping the RPi, to be sure that it's in the local network
```bash
ping -c 5 pawn.local
PING pawn.local (192.168.18.23) 56(84) bytes of data.
64 bytes from 192.168.18.23: icmp_seq=1 ttl=64 time=7.55 ms
64 bytes from 192.168.18.23: icmp_seq=2 ttl=64 time=8.93 ms
64 bytes from 192.168.18.23: icmp_seq=3 ttl=64 time=6.45 ms
64 bytes from 192.168.18.23: icmp_seq=4 ttl=64 time=6.60 ms
64 bytes from 192.168.18.23: icmp_seq=5 ttl=64 time=6.55 ms

--- pawn.local ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4005ms
rtt min/avg/max/mdev = 6.452/7.214/8.927/0.943 ms
```

arp-scan
```bash
$ sudo apt install arp-scan
$ sudo arp-scan --interface=enp34s0 192.168.18.0/24

Interface: wlp0s20f3, type: EN10MB, MAC: dc:46:28:8b:14:c9, IPv4: 192.168.18.13
Starting arp-scan 1.10.0 with 256 hosts (https://github.com/royhills/arp-scan)
192.168.18.1    f8:9b:6e:a0:3f:c0       Nokia Solutions and Networks GmbH & Co. KG
192.168.18.10   d8:bb:c1:66:02:c8       Micro-Star INTL CO., LTD.
192.168.18.11   30:9c:23:49:91:a3       Micro-Star INTL CO., LTD.
192.168.18.4    78:c1:ae:5e:b4:26       Hangzhou Ezviz Software Co.,Ltd.
192.168.18.19   0c:73:eb:52:b9:9f       Husty M.Styczen J.Hupert Sp.J.
192.168.18.3    70:f7:54:50:67:88       AMPAK Technology,Inc.
192.168.18.23   2c:cf:67:bf:e2:ec       (Unknown)
```

Also, the following command can be used:  
```bash
$ sudo arp-scan --interface=wlp0s20f3 --localnet 
```

### Python Network Discovery Script

For a more comprehensive network discovery tool, you can use the Python script included in this repository. This script provides more detailed information about devices in your network, including their hostnames.

#### Installing Dependencies

```bash
# Install required Python packages
pip install scapy netifaces zeroconf
```

#### Using the Script

```bash
# Navigate to the scripts directory
cd scripts

# Run the script with default settings
./discover_hosts.py

# Run with verbose output
./discover_hosts.py --verbose

# Specify a network interface
./discover_hosts.py --interface eth0

# Specify a subnet to scan
./discover_hosts.py --subnet 192.168.1.0/24
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

This script is particularly useful for identifying all Raspberry Pi nodes in your cluster by their hostnames.

SSH to the RPi
```bash
$ ssh artur@pawn.local
The authenticity of host 'pawn.local (192.168.18.24)' can't be established.
ED25519 key fingerprint is SHA256:ypSChuHB0IsqUYX46RrXNtdZr03Ng/a8Rz1khz8XHX4.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'pawn.local' (ED25519) to the list of known hosts.
artur@pawn.local's password: 
Linux pawn 6.12.25+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.12.25-1+rpt1 (2025-04-30) aarch64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue May 13 02:17:59 2025

artur@pawn:~ $ df -Th
Filesystem     Type      Size  Used Avail Use% Mounted on
udev           devtmpfs  3.9G     0  3.9G   0% /dev
tmpfs          tmpfs     806M   16M  791M   2% /run
/dev/mmcblk0p2 ext4       28G  4.9G   22G  19% /
tmpfs          tmpfs     4.0G  400K  4.0G   1% /dev/shm
tmpfs          tmpfs     5.0M   48K  5.0M   1% /run/lock
/dev/mmcblk0p1 vfat      510M   77M  434M  16% /boot/firmware
tmpfs          tmpfs     806M  208K  805M   1% /run/user/1000
```

Updating and upgrading
Good option is to create the `update_software.sh` script and run it when needed
```bash
echo "[1. Updating and upgrading (apt) ......]" &&
sudo apt update &&
sudo apt upgrade &&
sudo apt dist-upgrade &&
echo "" &&
echo "[2. Cleaning Up ......]" &&
sudo apt autoremove &&
sudo apt autoclean &&
sudo apt clean && 
sudo apt autopurge &&
echo "" &&
echo "[3. Done ......!!!!]" &&
echo ""
```

At the first running of the updating script it may take some time, but later it will not take too long.
It's almost sure that system must be rebooted after script finishes its job:  
```bash
$ sudo reboot
```
