# scompiler

scompiler is a python program to compile some programs and save text and image
output.

The code is compiler and/or run in temporal directory `/tmp/scompiler/`.

# Features

Support:

- LaTeX
- Mbed
- Python

# Packaging

- **Gentoo:** imperium repository.

# Requirements

In order to use you need install:

| Language | Requirements |
|----------|--------------|
| LaTeX    | texlive      |
|          | exiftool     |
| Mbed     | mbed-tools   |
|          | gcc(arm)     |
| Python   | python       |

# Installation

To install the Python library and the command line utility, run:

```bash
python3 -m build
pip install dist/*.whl
```

# Running

## LaTeX

The recommended structure is one main file.

```
document_name/
├── files/
│   ├── chapter_1/
│   │   ├── main.tex
│   │   ├── section_1.tex
│   │   └── section_2.tex
│   └── main.tex
├── images/
└── report.tex
```

The bibliography use `biber`.

The pdf is save in `/tmp/` with the name from main `tex` file.

## Mbed

The first time is create symbolic link to build directory `cmake_build/`. That
is save in `/tmp/scompiler/`.

Is recommended use symbolic link to `mbed-os/` for the project size.

The binary is save in `/tmp/` with the prefix `stm_<name_project>.bin`.

## Python

### Script

Copy and run script.

### Package

Create a directory to virtual `env` where the package is installed
`/tmp/scompiler-test-py/`.

To activate the `venv` run:

```
source /tmp/scompiler-test-py/.venv/bin/activate
```
