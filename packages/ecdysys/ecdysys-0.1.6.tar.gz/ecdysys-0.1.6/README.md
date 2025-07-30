# Ecdysys

Little CLI tool to print and update system
Currently supported package managers are:
- `pacman` (requires `pacman-contrib` as well)
- `yay` and `paru` (aur support)
- `flatpak`

[<img alt="github" height="56" src="https://cdn.jsdelivr.net/npm/@intergrav/devins-badges@3/assets/cozy/available/github_vector.svg">](https://github.com/claymorwan/ecdysys)
[<img alt="pypi" height="56" src="https://cdn.jsdelivr.net/npm/@intergrav/devins-badges@3/assets/cozy/available/pypi_vector.svg">](https://pypi.org/project/ecdysys/)
[<img alt="aur" height="56" src="./assets/cozy_vector.svg">](https://aur.archlinux.org/packages/python-ecdysys)



## Installation
### From Pypi
```shell
pip install ecdysys
```
### From the Aur
```shell
paru -S python-ecdysys
```
2. Create a `config.toml` file, these are the following entry available

| Entry                    | Usage                                                     | Valid entry                                           | Example                       |
|--------------------------|-----------------------------------------------------------|-------------------------------------------------------|-------------------------------|
| `pkg_managers`*          | package manager to use                                    | any of the supported package manager (list of string) | `[ "pacman", "flatpak" ]`     |
| `aur_helper`             | aur helper to use (`pacman` must be set in `pkg_managers` | any of the supported aur helper (string)              | `"paru"`                      |
| `post_install_script`    | path to script ot run after installation                  | path to file (string)                                 | `path/to/script`              |
| `args_<package manager>` | arguments for any of the selected package manager         | string                                                | `args_pacman = "--noconfirm"` |

*Must be set

## Usage
```
usage: ecdysys [-h] [-v] [-l] [-u] [--no-spinner]

Python CLI to update your system packages

options:
  -h, --help     show this help message and exit
  -v, --version  Print version
  -l, --list     List available updates
  -u, --update   Update package
  --no-spinner   Doesn't show spinner when listing updates
```