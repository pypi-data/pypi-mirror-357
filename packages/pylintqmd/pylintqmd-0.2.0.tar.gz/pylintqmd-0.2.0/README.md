⚠️ **This package is now deprecated. Please use [lintquarto](https://github.com/lintquarto/lintquarto) instead, which provides support for a wider range of linters.**

<br>
<br>
<br>

---

<div align="center">

# pylintqmd

![Code licence](https://img.shields.io/badge/🛡️_Code_licence-MIT-8a00c2?style=for-the-badge&labelColor=gray)
[![ORCID](https://img.shields.io/badge/ORCID_Amy_Heather-0000--0002--6596--3479-A6CE39?style=for-the-badge&logo=orcid&logoColor=white)](https://orcid.org/0000-0002-6596-3479)
[![PyPI](https://img.shields.io/pypi/v/pylintqmd?style=for-the-badge&labelColor=gray)](https://pypi.org/project/pylintqmd/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.15727754-486CAC?style=for-the-badge&logoColor=white)](https://doi.org/10.5281/zenodo.15727754)

</div>

<br>

Package for running [pylint](https://github.com/pylint-dev/pylint) on quarto `.qmd` files.

<br>

## Installation

You can install `pylintqmd` from [PyPI](https://pypi.org/project/pylintqmd/):

```
pip install pylintqmd
```

This package requires [pylint](https://github.com/pylint-dev/pylint) to function. When you install `pylintqmd` via pip, `pylint` will be installed automatically. You do not need to manually install any other dependencies.

<br>

## Getting started using `pylintqmd`

To lint current directory and sub-directories:

```
pylintqmd .
```

To lint file:

```
pylintqmd file.qmd
```

To lint all .qmd files in directory

```
pylintqmd folder
```

To keep temporary .py files for debugging when lint:
```
pylintqmd . -k
pylintqmd . --keep-temp
```

<br>

## Community

Curious about contributing? Check out the [contributing guidelines](CONTRIBUTING.md) to learn how you can help. Every bit of help counts, and your contribution - no matter how minor - is highly valued.

<br>

## How to cite `pylintqmd`

Please cite the repository on GitHub and/or Zenodo:

> Heather, A. (2025). pylintqmd (v0.2.0).  https://github.com/amyheather/pylintqmd.
>
> Heather, A. (2025). pylintqmd (v0.2.0). https://doi.org/10.5281/zenodo.15727754.

Citation instructions are also provided in `CITATION.cff`.

<br>

## Acknowledgements

Parts of this package were generated or adapted from code provided by [Perplexity](https://www.perplexity.ai/).