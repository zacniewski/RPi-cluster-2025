## Installing GitLab in a Docker container
> I'm not going to touch on this topic for now, because I will most likely develop it further in another project!!!


### 1. Links

  - [official](https://docs.gitlab.com/install/docker/) documentation from Gitlab,
  - [official](https://hub.docker.com/r/gitlab/gitlab-ce/) Docker image from GitLab,

### 2. Create a directory for the volumes
> I'll be using the `queen` machine for Gitlab installation.

  - Create the directory:
```shell
$ sudo mkdir -p /srv/gitlab
```
  - add the following line at the end of `~/.bashrc` (or other depending on your shell) file:
```sh
export GITLAB_HOME=/srv/gitlab
```
  - source the file above and check the `GITLAB_HOME` variable:
```shell
$ source ~/.bashrc
$ echo $GITLAB_HOME
/srv/gitlab
```

  - check the "fresh" [tag](https://hub.docker.com/r/gitlab/gitlab-ce/tags) value of the Gitlab Community Edition Docker image
  - in the day of writing it was `18.6.1-ce.0`

### 3. Create docker-compose.yml file
```yaml
version:
```

- after first run of `docker-compose` with sudo:
```shell
$ sudo docker compose up -d
WARN[0000] The "GITLAB_HOME" variable is not set. Defaulting to a blank string.
```
  - the solution [https://askubuntu.com/questions/1531325/docker-compose-is-not-picking-up-variable-that-i-defined-in-my-shell] suggests to use the `--env-file` parameter with newly created `docker.env` file,
  - `docker.env` file:
```sh
GITLAB_HOME=/srv/gitlab
```
- change the SSH port to different from default (22):
  - open `/etc/ssh/sshd_config` with your editor, and change the SSH port:
   ```bash
  Port = 2424
  ```
  - save the file and restart the SSH service:
  ```shell
  sudo systemctl restart ssh
  ```
- now to connect from outside to our machine we need to use the port we set in the `sshd_config` file:
```shell
ssh artur@queen-cluster.local -p 2424
```
- then our command would be: `sudo docker compose --env-file ./docker.env up -d`.
