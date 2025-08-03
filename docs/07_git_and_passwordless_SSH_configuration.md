## Git on the Raspberry Pis

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
