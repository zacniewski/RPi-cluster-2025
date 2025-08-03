# RPi-cluster-2025

Description of the process of building Raspberry Pi cluster
<!-- Improved compatibility of back to a top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or open an issue with the tag "enhancement".
*** Remember to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/zacniewski/RPi-cluster-2025">
    <img src="images/raspberry_pi_icon_80px.png" alt="Logo RPi">
  </a>

<h3 style="align:center">Rasperry Pi cluster</h3>

  <p style="align:center">
    The project shows creating the Raspberry Pi cluster from scratch
    <br />
    <a href="https://github.com/zacniewski/RPi-cluster-2025/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/zacniewski/RPi-cluster-2025">View Demo</a>
    &middot;
    <a href="https://github.com/zacniewski/RPi-cluster-2025/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/zacniewski/RPi-cluster-2025/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

:zap: For some time now, I've been tempted to build a cluster using Raspberry Pi minicomputers.
:muscle: To experiment with network configuration, containerization, web applications, CI/CD, distributed computing, and a few other interesting topics.
:wink: I hope the information in the following documentation will be useful to some people.
<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![RPi][RPi.com]][RPi-url]
* [![Nginx][Nginx.org]][Nginx-url]
* [![Django][Django.com]][Django-url]
* [![Docker][Docker.com]][Docker-url]
* [![Spark][Spark.org]][Spark-url]
* [![Github][Github.com]][Github-url]
* [![Gitlab][Gitlab.com]][Gitlab-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![AlpineJS][Alpine.js]][Alpine-url]

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

:information_source: All things needed to start are mentioned at the beginning of the documentation.
:information_source: The operating system used in this project is Linux.
:information_source: All used software is free software, under a different type of licenses.

### Prerequisites

:information_source: I've used four Raspberry Pi 5 microcomputers to build a cluster.
:information_source: You can use a small local networ of PCs (or laptops) with Unix-based systems to do some experiments, etc.
:information_source: Of course, you don't have to do it, but you can use this project to build your version of cluster or to get some tips and tricks from my experience.


### Installation

1. Read the [documentation](https://github.com/zacniewski/RPi-cluster-2025/tree/main/docs).
2. Clone the repo.
   ```sh
   git clone https://github.com/zacniewski/RPi-cluster-2025.git
   ```
3. Manage IP addresses of your machines in the local network.

4. Install necessary software (described in the documentation).
  - Docker,
  - uv.

5. Install Python packages.
  - create virtual environment with `uv` or `pip`,
  - activate it,
  - install packages.

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Putting everything together (RPi, power supplies, drives, cables, etc.)
- [x] Installing the operating system on a micro SD card
- [x] Installing the operating system on NVMe drives
    - [x] Configuring IP addresses in the local network
- [x] Installing Docker on Raspberry Pi
- [ ] Django web application for cluster monitoring
    - [ ] Using uv for managing packages
- [ ] Installation of distributed computing software
    - [ ] .........
- [ ] Connecting cameras and external sensors
    - [ ] .........
- [ ] VPN installation and configuration
    - [ ] .........


See the [open issues](https://github.com/zacniewski/RPi-cluster-2025/issues) for a full list of proposed features (and known issues).

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/zacniewski/RPi-cluster-2025/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=zacniewski/RPi-cluster-2025" alt="contrib.rocks image" />
</a>



<!-- LICENSE.txt -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Artur Zacniewski - [@zacniewski](https://x.com/zacniewski) - a.zacniewski@we.umg.edu.pl

Project Link: [https://github.com/zacniewski/RPi-cluster-2025](https://github.com/zacniewski/RPi-cluster-2025)

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
Below are some links, that I've found useful during the process of creating this project:
* [Best README template](https://github.com/othneildrew/Best-README-Template/blob/main/README.md)
* [Custom badges with Shield.io](https://javascript.plainenglish.io/how-to-make-custom-language-badges-for-your-profile-using-shields-io-d2aeaf016b6b)
* [Simple Icons](https://simpleicons.org/)
* [Raspberry Pi logo/wallpaper](https://www.deviantart.com/onix5/art/Raspberry-Pi-Logo-Wallpaper-4K-739821936)
* [Raspberry Pi icon](https://icon-icons.com/icon/raspberry-pi/198019)
* [Chess icons](https://fontawesome.com/search?q=chess&o=r&ic=free) from FontAwesome

<p style="align:right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/zacniewski/RPi-cluster-2025.svg?style=for-the-badge
[contributors-url]: https://github.com/zacniewski/RPi-cluster-2025/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/zacniewski/RPi-cluster-2025.svg?style=for-the-badge
[forks-url]: https://github.com/zacniewski/RPi-cluster-2025/network/members
[stars-shield]: https://img.shields.io/github/stars/zacniewski/RPi-cluster-2025.svg?style=for-the-badge
[stars-url]: https://github.com/zacniewski/RPi-cluster-2025/stargazers
[issues-shield]: https://img.shields.io/github/issues/zacniewski/RPi-cluster-2025.svg?style=for-the-badge
[issues-url]: https://github.com/zacniewski/RPi-cluster-2025/issues
[license-shield]: https://img.shields.io/github/license/zacniewski/RPi-cluster-2025?style=for-the-badge
[license-url]: https://github.com/zacniewski/RPi-cluster-2025/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/artur-zacniewski-29436928
[product-screenshot]: images/raspberry_pi_logo_wallpaper_4k_by_onix5_dc8gy9c-pre.jpg

[RPi.com]: https://img.shields.io/badge/-RaspberryPi-C51A4A?style=for-the-badge&logo=Raspberry-Pi
[RPi-url]: https://www.raspberrypi.com/
[Nginx.org]: https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white&style=for-the-badge
[Nginx-url]: https://nginx.org/
[Django.com]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[Docker.com]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Spark.org]: https://img.shields.io/badge/ApacheSpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white
[Spark-url]: https://spark.apache.org/
[Github.com]: https://img.shields.io/badge/GitHub-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
[Github-url]: https://github.com
[Gitlab.com]: https://img.shields.io/badge/GitLab-FC6D26?style=for-the-badge&logo=gitlab&logoColor=white
[Gitlab-url]: https://gitlab.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[Alpine.js]: https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpinedotjs&logoColor=white
[Alpine-url]: https://alpinejs.dev/
[twitter_handle]: zacniewski
