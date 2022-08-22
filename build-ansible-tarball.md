# Ansible Upstream PyPi Release Steps

## Requirements
---------------
- Docker

## Build Steps
---------------
Pull python:3.10 docker image
```bash
docker pull python:3.10
```

Start and exec docker container
```bash
docker run -it –name=ansible-community python:3.10 bash
docker exec -it ansible-community bash
```

Install ansible-core antsibull
```bash
pip install ansible-core antsibull
```

Install community.general 
```bash
ansible-galaxy install community.general
```

Clone antsibull repo
```bash
git clone https://github.com/ansible-community/antsibull
cd antsibull
```

Run the build release playbook to create ansible tar
```bash
ansible-playbook playbooks/build-single-release.yaml -e antsibull_ansible_git_version=stable-2.13 -e antsibull_ansible_version=6.3.0
```

> _**Note:** For Ansible 7 & Ansible-core 2.14 use `antsibull_ansible_git_version=stable-2.14` `antsibull_ansible_version=7.0.0`_

Playbook creates `builds` directory and clones `ansible` & `ansible-build-data` repos and also generates ansible-6.3.0* tar and wheels package

To sign and upload newly created ansible-6.3.0* to PyPI, download `armored-signing.key` from _Bitwaden Red Hat Ansible_ account and import the gpg signing subkey.
```bash
gpg --import armored-signing.key
```

```bash
twine upload --sign --identity "ansible-gha@redhat.com" ansible-6.3.0*
```

Adding `--sign` options makes `twine` to sign and upload the packages to PyPi.