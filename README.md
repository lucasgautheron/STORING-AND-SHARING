# Managing, storing and sharing long-form recordings and their annotations

## Explanations

This repository contains the source of the paper "Managing, storing and sharing long-form recordings and their annotations"
by Lucas Gautheron et al.

It demonstrates how the use of [DataLad](https://www.datalad.org/) combined with the [ChildProject package](https://childproject.readthedocs.io/en/latest/)
helps design reproducible research on day-long recordings of children.

This repository has been built upon the [Automatically Reproducible Paper Template](https://github.com/datalad-handbook/repro-paper-sketch/) by Adina Wagner.


## Reproducing the paper

Before anything, make sure you have installed DataLad (see [here](https://childproject.readthedocs.io/en/latest/install.html) for instructions).

1. Install the repository with DataLad:

```bash
datalad install -r git@gin.g-node.org:/LAAC-LSCP/managing-storing-sharing-paper.git
cd managing-storing-sharing-paper
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Cleanup generated files

```bash
make clean
```

4. Trigger the build

```bash
make main.pdf
```