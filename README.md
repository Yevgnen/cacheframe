# Table of Contents <span class="tag" tag-name="TOC"><span class="smallcaps">TOC</span></span>

- [Introduction](#introduction)
- [Installation](#installation)
  - [From pip](#from-pip)
  - [From source](#from-source)
- [Usage](#usage)
  - [Example](#example)
- [Contribution](#contribution)
  - [Formatting Code](#formatting-code)

# Introduction

Simple Pandas dataframe file cache.

# Installation

## From pip

``` bash
pip install cacheframe
```

## From source

``` bash
pip install git+https://github.com/Yevgnen/cacheframe.git
```

# Usage

The only provided function decorator is `cacheframe.cacheframe` with the following arguments:

- `cache_dir`: directory to place cache files (default: `.cache`)
- `file`: cache file name, support file types are: `.csv`, `.xlxs`, `.pickle`, `.json`, `.parquet` and `.feather` (default: `dataframe.parquet`)
- `read_kwds`: optional keyword arguments passed to readers (`pandas.to_*`) when reading cache (default: `None`)
- `write_kwds`: optional keyword arguments passed to writers (`pandas.read_*`) when writing cache (default: `None`)
- `ttl`: optional TTL value to invalid cache (default: `None`)
- `disable`: boolean indicator to enable or disable cache (default: `False`)

The wrapped function should return single dataframe.

Note that as Pandas does NOT install required engines for reading or writing specific file types, you maybe need to install them manually, e.g. `pyarrow` for `.feather`, `fastparquet` for `.parquet`, `openpyxl` for `.xlsx` …

## Example

``` python
# -*- coding: utf-8 -*-

import time

import pandas as pd
from pandas import DataFrame

from cacheframe import cacheframe


@cacheframe(cache_dir=".cache", file="dataframe.parquet", ttl=3)
def read_large_dataframe() -> DataFrame:
    print("Reading a very large dataframe...")
    time.sleep(2)

    df = pd.DataFrame([{"x": 1, "y": 2}, {"x": 99, "y": 100}])

    return df


if __name__ == "__main__":
    print("Read once...")
    df = read_large_dataframe()  # "Reading dataframe..."
    print(df)

    print("Read again...")
    df = read_large_dataframe()  # Cache is read
    print(df)

    print("Wait 5 seconds and read again...")
    time.sleep(5)
    df = read_large_dataframe()  # Cache expired, "Reading dataframe..."
    print(df)
```

# Contribution

## Formatting Code

To ensure the codebase complies with a style guide, please use [flake8](https://github.com/PyCQA/flake8), [black](https://github.com/psf/black) and [isort](https://github.com/PyCQA/isort) tools to format and check codebase for compliance with PEP8.
