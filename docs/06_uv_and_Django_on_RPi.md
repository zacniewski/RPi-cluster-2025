## uv installation on RPi   

#### 1. Installation process
- for years `pip` + `venv` was my simple, but effective way to work with Python web applications (especially in Django),  
- this time `uv` will be the main tool for Python ecosystem :snake:,  
- I've used many tips from [Saas Pegasus](https://www.saaspegasus.com/guides/uv-deep-dive/) guide on `uv`, 
- first, the `uv` must be installed:  
```bash
artur@pawn-cluster:~ $ curl -LsSf https://astral.sh/uv/install.sh | sh
downloading uv 0.7.21 aarch64-unknown-linux-gnu
no checksums to verify
installing to /home/artur/.local/bin
  uv
  uvx
everything's installed!

To add $HOME/.local/bin to your PATH, either restart your shell or run:

    source $HOME/.local/bin/env (sh, bash, zsh)
    source $HOME/.local/bin/env.fish (fish)
artur@pawn-cluster:~ $ source $HOME/.local/bin/env
artur@pawn-cluster:~ $ uv --version
uv 0.7.21
```

- I've also installed `uv` on my PC, where I'll be developing the Django project,  
- to get information about `uv` commands just use:  
```bash 
uv --help
```

- I'll start from the traditional version - with `SQLite` database and development server (it will be later modified and improved),   
```bash
$ uv init django_rpi_cluster
Initialized project `django-rpi-cluster` at `/home/artur/Desktop/PROJECTS/RPi-cluster-2025/django_rpi_cluster
 
$ cd django_rpi_cluster/
$ uv sync

Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Creating virtual environment at: .venv
Resolved 1 package in 2ms
Audited in 0.00ms

$ uv add django                                                                                                                                                                                       
Resolved 5 packages in 563ms
Prepared 3 packages in 1.36s
Installed 3 packages in 175ms
 + asgiref==3.9.1
 + django==5.2.4
 + sqlparse==0.5.3
```

- we can check installed packages with `uv tree`:  
```bash
$ uv tree                                                                                                                                                                                       
Resolved 5 packages in 1ms
django-rpi-cluster v0.1.0
└── django v5.2.4
    ├── asgiref v3.9.1
    └── sqlparse v0.5.3
```

- starting a new Django project:  
```bash
$ uv run django-admin startproject core .
$ uv run manage.py runserver                                                                                                                                                                          

Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.                                                   
Run 'python manage.py migrate' to apply them.
July 16, 2025 - 18:14:17
Django version 5.2.4, using settings 'core.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

- let's add an application called `monitoring`:  
```bash
$ uv run manage.py startapp monitoring
```

- let's install the [psutil](https://github.com/giampaolo/psutil) package that will be used for process and system monitoring:  
```bash
$ uv add psutil
```

- let's add the [python-decouple](https://pypi.org/project/python-decouple/) package that helps you to organize your settings so that you can change parameters without having to redeploy your app:  
```bash
$ uv add python-decouple
```

- now we need to create `.env` file and store there vulnerable parameters and credentials,  
- all information about using `python-decouple` is available in the aforementioned documentation!
> Of course, we must add the `.env` to `.gitignore`!


- to update `uv`:  
```bash
$ uv self update
info: Checking for updates...
success: Upgraded uv from v0.7.21 to v0.8.0! https://github.com/astral-sh/uv/releases/tag/0.8.0

```