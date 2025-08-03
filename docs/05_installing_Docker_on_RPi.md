## Docker installation on RPi

#### 1. Installation process
- official [documentation](https://docs.docker.com/engine/install/raspberry-pi-os/) is for a 32-bit systems,
- our machines are 64-bit (arm64) versions of RPi,
- on the documentation page, we have information about our case:
> If you're using the 64-bit (arm64) version, follow the instructions for Debian.

- on the official documentation [page](https://docs.docker.com/engine/install/debian/) for Debian, we have few options of Docker installation,
- I choose the [apt repository](https://docs.docker.com/engine/install/debian/#install-using-the-repository) option because i.a. it's useful to see the steps necessary to install Docker using the package repository,  and have the new version of Docker checked with every running of updates,
- the commands from the official documentation are as follows:

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- if everything goes fine with installation, we could try to run standard `hello-world` image,
- we could also chech the Docker's version:

```bash
artur@pawn-cluster:~ $ docker --version
Docker version 28.3.2, build 578ccf6
```

- if we look into the `/etc/apt/sources.list.d/docker.list` file, we could see the following line:
```
deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian   bookworm stable
```
- it means that the `$VERSION_CODENAME` variable from the installation commands was replaced by `bookworm`, which is of course the codename of Debian 12 version :smiley:


#### 2. Post-installation steps
- optional post-installation [procedures](https://docs.docker.com/engine/install/linux-postinstall/) describe how to configure your Linux host machine to work better with Docker,
- since our project is rather scientific and will be working mainly in local network, we'll
- if you plan to work with the Docker in production, consider the [rootless](https://docs.docker.com/engine/security/rootless/) mode for your project,
> [security](https://docs.docker.com/engine/security/#docker-daemon-attack-surface) should have the highest priority!

- I'd like not to preface the `docker` command with `sudo` everytime, and that's why I'd like to manage Docker as a non-root user,
- it occurred that after installation of Docker the `docker` is already created:
```bash
artur@pawn-cluster:~ $ sudo groupadd docker
groupadd: group 'docker' already exists
```
- I've added my user to the `docker` group:
```bash
artur@pawn-cluster:~ $ sudo usermod -aG docker $USER
```
- after logging out and in I was able to run `docker` command without `sudo`:
```bash
artur@pawn-cluster:~ $ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
c9c5fd25a1bd: Pull complete
Digest: sha256:ec153840d1e635ac434fab5e377081f17e0e15afab27beb3f726c3265039cfff
Status: Downloaded newer image for hello-world:latest
```

- to check if the Docker service starts on boot, we can type after the start of the OS:
```bash
artur@pawn-cluster:~ $ sudo systemctl status docker.service

● docker.service - Docker Application Container Engine
     Loaded: loaded (/lib/systemd/system/docker.service; enabled; preset: enabled)
     Active: active (running) since Wed 2025-07-16 16:24:05 CEST; 2min 4s ago
TriggeredBy: ● docker.socket
       Docs: https://docs.docker.com
   Main PID: 1366 (dockerd)
      Tasks: 11
        CPU: 256ms
     CGroup: /system.slice/docker.service
             └─1366 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

Jul 16 16:24:05 pawn-cluster systemd[1]: Started docker.service - Docker Application Container Engine.
```
