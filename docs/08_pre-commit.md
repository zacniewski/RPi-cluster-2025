## Git hook scripts with pre-commit

- inside a Django project:
```shell
$ uv add pre-commit
Resolved 29 packages in 740ms
Prepared 9 packages in 1.35s
Installed 9 packages in 13ms
 + cfgv==3.4.0
 + distlib==0.4.0
 + filelock==3.18.0
 + identify==2.6.12
 + nodeenv==1.9.1
 + platformdirs==4.3.8
 + pre-commit==4.2.0
 + pyyaml==6.0.2
 + virtualenv==20.32.0
```
- the [documentation](https://pre-commit.com/#install) page,
- creating configuration file:
```shell
$ touch .pre-commit-config.yaml
```

- based on the documentation of `pre-install` starting file could look like this:
```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
    -   id: check-yaml
    -   id: end-of-file-fixer
    -   id: trailing-whitespace
```

- we have to install `pre-commit`:
```shell
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

- it's usually a good idea to run the hooks against all the files when adding new hooks (usually pre-commit will only run on the changed files during git hooks):
```shell
$ pre-commit run --all-files
[INFO] Initializing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
check yaml...........................................(no files to check)Skipped
fix end of files.........................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing django_rpi_cluster/monitoring/tests/conftest.py
Fixing docs/README.md
Fixing docs/01_equipment_before_unpacking.md
Fixing django_rpi_cluster/monitoring/templates/monitoring/system_parameters.html
Fixing .gitignore
...............................................................................

trim trailing whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing django_rpi_cluster/monitoring/tests/conftest.py
Fixing docs/README.md
Fixing docs/01_equipment_before_unpacking.md
Fixing django_rpi_cluster/monitoring/templates/monitoring/system_parameters.html
Fixing .gitignore
```

- after fixing the issues in the code by `pre-commit`, we can check files again:
```shell
$ pre-commit run --all-files
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
```
- you can add the hooks you need,
- before every commit your files will be checked with installed hooks.
