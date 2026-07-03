# Documentation

This folder contains the build log for the cluster. Read [`00_overview.md`](00_overview.md) first, then follow the numbered pages in order.

## Table of Contents
- [Reading Order](#reading-order)
- [Document Map](#document-map)
- [Visuals](#visuals)
- [Back to Repo](#back-to-repo)

## Reading Order
The docs are numbered to match the build sequence:
1. hardware and unpacking,
2. operating system installation,
3. Docker and Python tooling,
4. SSH, Git, and automation,
5. optional services and references.

## Document Map
| Order | File | What it covers |
| --- | --- | --- |
| 00 | [00_overview.md](00_overview.md) | Project summary and build flow |
| 01 | [01_equipment_before_unpacking.md](01_equipment_before_unpacking.md) | Equipment list and costs |
| 02 | [02_after_unpacking.md](02_after_unpacking.md) | Photos from unpacking and assembly |
| 03 | [03_installing_OS_on_RPi-SD-card.md](03_installing_OS_on_RPi-SD-card.md) | Raspberry Pi OS on SD cards |
| 04 | [04_installing_OS_on_RPi-NVMe_disk.md](04_installing_OS_on_RPi-NVMe_disk.md) | Raspberry Pi OS on NVMe disks |
| 05 | [05_installing_Docker_on_RPi.md](05_installing_Docker_on_RPi.md) | Docker installation and verification |
| 06 | [06_uv_and_Django_on_RPi.md](06_uv_and_Django_on_RPi.md) | `uv` and Django setup |
| 07 | [07_git_and_passwordless_SSH_configuration.md](07_git_and_passwordless_SSH_configuration.md) | Git and passwordless SSH |
| 08 | [08_pre-commit.md](08_pre-commit.md) | Pre-commit hooks |
| 09 | [09_Gitlab_in_Docker_container.md](09_Gitlab_in_Docker_container.md) | Optional GitLab container |
| 10 | [10_links.md](10_links.md) | Useful external links |
| 11 | [11_my_additional_devices_for_optional_usage.md](11_my_additional_devices_for_optional_usage.md) | Optional devices |

## Visuals
The docs reuse the photos and screenshots from `../images/` so each step can be matched to the physical build.

![Cluster hardware](../images/RPi_tower_2.jpg)

![Monitoring dashboard](../images/dashboard.png)

## Back to Repo
Return to the main project page in [`../README.md`](../README.md).
