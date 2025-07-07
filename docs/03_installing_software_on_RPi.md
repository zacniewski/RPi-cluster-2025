## Software installation for RPi cluster  

1. RPi Imager  
- link to [official page](https://www.raspberrypi.com/software/),  
- link to [GitHub](https://github.com/raspberrypi/rpi-imager).  

obrazki z instalacji OS

Intefejsy sieciowe
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

arp-scan
```bash
$ sudo apt install arp-scan
$ sudo arp-scan --interface=enp34s0 192.168.18.0/24
```

ping
```bash
ping -c 5 pawn.local
PING pawn.local (192.168.18.24) 56(84) bytes of data.
64 bytes from 192.168.18.24: icmp_seq=1 ttl=64 time=1.33 ms
64 bytes from 192.168.18.24: icmp_seq=2 ttl=64 time=4.09 ms
64 bytes from 192.168.18.24: icmp_seq=3 ttl=64 time=3.38 ms
64 bytes from 192.168.18.24: icmp_seq=4 ttl=64 time=3.32 ms
64 bytes from 192.168.18.24: icmp_seq=5 ttl=64 time=1.78 ms

--- pawn.local ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4004ms
rtt min/avg/max/mdev = 1.326/2.780/4.094/1.048 ms
```

SSH
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