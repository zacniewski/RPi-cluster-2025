# Git and passwordless SSH configuration

## Table of Contents
- [Installing Git](#1-installing-git)
- [Git user information](#2-setting-user-information-in-git-configuration)
- [Generating SSH keys](#3-generating-ssh-keys)
- [SSH aliases](#4-ssh-aliases)
- [Hostname resolution](#5-hostname-resolution)
- [Verification](#6-verification)

#### 1. Installing git

```shell
artur@queen-cluster:~ $ sudo apt install git
```

#### 2. Setting user information in git configuration

- on every machine we should set the proper information for a version control system:
```shell
artur@queen-cluster:~ $ git config --list
artur@queen-cluster:~ $ git config --global user.name "Artur Zacniewski"
artur@queen-cluster:~ $ git config --global user.email "a.zacniewski@gmail.com"
artur@queen-cluster:~ $ git config --list
user.name=Artur Zacniewski
user.email=a.zacniewski@gmail.com
```

#### 3. Generating SSH keys
- we can follow, for example, the GitHub [guide](https://docs.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent):
```shell
$ ssh artur@pawn-cluster.local
artur@pawn-cluster.local's password:

artur@pawn-cluster:~ $ ssh-keygen -t ed25519 -C "a.zacniewski@gmail.com"
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/artur/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/artur/.ssh/id_ed25519
Your public key has been saved in /home/artur/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:Jq86/VZYOqCU6tePAKlloIt4F/z3UU5zilS8d28HolI a.zacniewski@gmail.com
The key's randomart image is:
+--[ED25519 256]--+
|                 |
|           .     |
|.    .      o    |
|.. oo .   .. .   |
|. =oo...S+E * + .|
|o=...o ++o.* * o.|
|=.. oo. +o+ o   +|
| ...o.o+.o .   ..|
|   ..oo+o .      |
+----[SHA256]-----+

artur@pawn-cluster:~ $ eval "$(ssh-agent -s)"
Agent pid 2355

artur@pawn-cluster:~ $ ssh-add ~/.ssh/id_ed25519
Identity added: /home/artur/.ssh/id_ed25519 (a.zacniewski@gmail.com)
```

- we can use the `ssh-copy-id` tool to copy the public key to other machines,
- this command will copy the public key from your client device to the `~/.ssh/authorized_keys` file on your Raspberry Pi,
- during this process, you will be prompted for your Raspberry Pi’s password to complete the operation,
- a useful guide was found [here](https://www.luisllamas.es/en/how-to-connect-ssh-without-password-by-generating-an-ssh-key-on-raspberry-pi/).
```shell
artur@pawn-cluster:~ $ ssh-copy-id artur@knight-cluster.local
The authenticity of host 'knight-cluster.local (192.168.1.102)' can't be established.
ED25519 key fingerprint is SHA256:/xX1rgRO/xkFJzgc9DvTQkfRFI5x6KBCJBXd5VEo2hk.
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:1: [hashed name]
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
artur@knight-cluster.local's password:

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'artur@knight-cluster.local'"
and check to make sure that only the key(s) you wanted were added.
```

- copy the public key to all your devices you'll be using, also the one you were using to generate the SSH keys,
- if everything went fine, we should SSH to another RPi without being prompted for a password:
```shell
artur@pawn-cluster:~ $ ssh artur@knight-cluster.local
Linux knight-cluster 6.12.34+rpt-rpi-2712
#1 SMP PREEMPT Debian 1:6.12.34-1+rpt1~bookworm (2025-06-26) aarch64
...
```
- this process must be repeated for every machine you want to use,
- after successfully adding keys, we can verify the `authorized_keys` file on each machine:
```shell
artur@queen-cluster:~ $ cd .ssh/
artur@queen-cluster:~/.ssh $ ls -lah
total 28K
drwx------  2 artur artur 4.0K Aug  9 20:08 .
drwx------ 17 artur artur 4.0K Aug  9 19:38 ..
-rw-------  1 artur artur  416 Aug  9 20:08 authorized_keys
-rw-------  1 artur artur  419 Aug  9 20:01 id_ed25519
-rw-r--r--  1 artur artur  104 Aug  9 20:01 id_ed25519.pub
-rw-------  1 artur artur 3.9K Aug  9 20:08 known_hosts
-rw-------  1 artur artur 3.1K Aug  9 20:07 known_hosts.old
artur@queen-cluster:~/.ssh $ cat authorized_keys
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDDU/2wKlyU3cACleUfruWbtCW8YUzRQFoQJld6rAGzG a.zacniewski@gmail.com
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMVQGxPjuVEsY3/YhyxOpTew+TUHsBKONypgcJT4K+MW a.zacniewski@gmail.com
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA3Lo9v6ANeNvGyzWk/ei1P1xyYco0uG6BukIYWB44Pk a.zacniewski@gmail.com
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIInxmc0utaKmfmW8NTS+s9At7Zx5OZhjUUp/3iigu87+ a.zacniewski@gmail.com
```
- some useful tips could be found [here](https://medium.com/analytics-vidhya/build-raspberry-pi-hadoop-spark-cluster-from-scratch-c2fa056138e0),
- we should be able to SSH to any of them without being prompted for a password:
```shell
artur@knight-cluster:~ $ ssh artur@pawn-cluster.local
Linux pawn-cluster 6.12.34+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.12.34-1+rpt1~bookworm (2025-06-26) aarch64
...
artur@pawn-cluster:~ $ ssh artur@rook-cluster.local
Linux rook-cluster 6.12.34+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.12.34-1+rpt1~bookworm (2025-06-26) aarch64
...
artur@rook-cluster:~ $ ssh artur@queen-cluster.local
Linux queen-cluster 6.12.34+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.12.34-1+rpt1~bookworm (2025-06-26) aarch64
...
artur@queen-cluster:~ $
```

#### 4. SSH aliases
- to simplify more, we can use SSH aliases,
- on every machine we should add the following lines to the `~/.ssh/config` file (create this file if it doesn't exist):
```shell
Host pawn-cluster
User artur
Hostname 192.168.1.101

Host knight-cluster
User artur
Hostname 192.168.1.102

Host rook-cluster
User artur
Hostname 192.168.1.103

Host queen-cluster
User artur
Hostname 192.168.1.104
```

#### 5. Hostname resolution
- also on every machine append the following lines to the `/etc/hosts` file (with `sudo` privileges):

```shell
192.168.1.101  pawn-cluster
192.168.1.102  knight-cluster
192.168.1.103  rook-cluster
192.168.1.104  queen-cluster
```
#### 6. Verification
- finally, restart the SSH service:
```shell
artur@pawn-cluster:~ $ sudo systemctl restart ssh
```
- and now we can SSH to any of the machines without being prompted for a password with shorter names:
```shell
artur@pawn-cluster:~ $ ssh knight-cluster
Linux knight-cluster 6.12.34+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.12.34-1+rpt1~bookworm (2025-06-26) aarch64
...
artur@knight-cluster:~ $
```
