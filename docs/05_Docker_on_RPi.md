## Docker installation on RPi   

#### 1. Official documentation is for a 32-bit system
- our machines are 64-bit (arm64) versions of RPi,  
- on the [Install Docker Engine on Raspberry Pi OS (32-bit)](https://docs.docker.com/engine/install/raspberry-pi-os/) page, we have information about our case:  
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
It means that the `$VERSION_CODENAME` variable from the installation commands was replaced by `bookworm`, which is of course the codename of Debian 12 version :smiley:  