# ngff-zarr

[![PyPI - Version](https://img.shields.io/pypi/v/ngff-zarr.svg)](https://pypi.org/project/ngff-zarr)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ngff-zarr.svg)](https://pypi.org/project/ngff-zarr)
[![Test](https://github.com/thewtex/ngff-zarr/actions/workflows/pixi-test.yml/badge.svg)](https://github.com/thewtex/ngff-zarr/actions/workflows/pixi-test.yml)
[![DOI](https://zenodo.org/badge/541840158.svg)](https://zenodo.org/badge/latestdoi/541840158)
[![Documentation Status](https://readthedocs.org/projects/ngff-zarr/badge/?version=latest)](https://ngff-zarr.readthedocs.io/en/latest/?badge=latest)
[![Give it a star!](https://img.shields.io/github/stars/thewtex/ngff-zarr?style=social)](https://github.com/thewtex/ngff-zarr)

A lean and kind
[Open Microscopy Environment (OME) Next Generation File Format (NGFF) Zarr implementation](https://ngff.openmicroscopy.org/latest/),
[OME-Zarr](https://link.springer.com/article/10.1007/s00418-023-02209-1).

## ✨ Features

- Minimal dependencies
- Work with arbitrary Zarr store types
- Lazy, parallel, and web ready -- no local filesystem required
- Process extremely large datasets
- Conversion of most bioimaging file formats
- Multiple downscaling methods
- Supports Python>=3.9
- Reads OME-Zarr v0.1 to v0.5 into simple Python data classes with Dask arrays
- Optional OME-Zarr data model validation during reading
- Writes OME-Zarr v0.4 to v0.5
- [Sharded Zarr] stores
- Optional writing via [tensorstore]

```{toctree}
:maxdepth: 2

quick_start.md
installation.md
python.md
cli.md
itk.md
methods.md
development.md
```

```{toctree}
:maxdepth: 3
:caption: 📖 Reference

apidocs/index.rst
```

[Sharded Zarr]: https://zarr.dev/zeps/accepted/ZEP0002.html
[tensorstore]: https://google.github.io/tensorstore/
