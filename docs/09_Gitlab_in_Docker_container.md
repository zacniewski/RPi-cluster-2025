# GitLab in a Docker container

This page is a planning note for a future expansion. The cluster can host GitLab, but the service is not part of the core build yet.

## Table of Contents
- [Scope](#scope)
- [Suggested setup](#suggested-setup)
- [Open questions](#open-questions)
- [References](#references)

## Scope
- Run the service on a dedicated node, most likely `queen`.
- Keep persistent data under `/srv/gitlab`.
- Start with the official GitLab CE container image.
- Use a separate SSH port only if the node needs remote access from outside the local network.

## Suggested setup
1. Create the volume directory.
   ```shell
   sudo mkdir -p /srv/gitlab
   ```
2. Export the home directory used by the compose file.
   ```sh
   export GITLAB_HOME=/srv/gitlab
   ```
3. Store the variable in a `docker.env` file when running compose from a non-interactive shell.
   ```sh
   GITLAB_HOME=/srv/gitlab
   ```
4. Pin the GitLab CE image tag once the deployment target is decided.
5. Start the stack with:
   ```shell
   sudo docker compose --env-file ./docker.env up -d
   ```

## Open questions
- Which node should host the service permanently?
- How much RAM and storage should be reserved for GitLab?
- What backup strategy should be used for `/srv/gitlab`?
- Should external SSH access use a non-default port, or should it stay LAN-only?

## References
- [GitLab Docker installation](https://docs.gitlab.com/install/docker/)
- [GitLab CE image on Docker Hub](https://hub.docker.com/r/gitlab/gitlab-ce/)
- [Compose environment-file note](https://askubuntu.com/questions/1531325/docker-compose-is-not-picking-up-variable-that-i-defined-in-my-shell)
