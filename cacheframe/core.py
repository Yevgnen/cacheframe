# -*- coding: utf-8 -*-

import functools
import logging
import os
from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Union

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)


@dataclass
class IO(object):
    reader: Callable
    writer: Callable


_IO_HELPERS = {
    ".csv": IO(pd.read_csv, DataFrame.to_csv),
    ".xlsx": IO(pd.read_excel, DataFrame.to_excel),
    ".pickle": IO(pd.read_pickle, DataFrame.to_pickle),
    ".pkl": IO(pd.read_pickle, DataFrame.to_pickle),
    ".json": IO(pd.read_json, DataFrame.to_json),
    ".parquet": IO(pd.read_parquet, DataFrame.to_parquet),
    ".feather": IO(pd.read_feather, DataFrame.to_feather),
}


def cacheframe(
    cache_dir: Union[str, os.PathLike] = ".cache",
    file: str = "dataframe.parquet",
    read_kwds: Optional[Mapping] = None,
    write_kwds: Optional[Mapping] = None,
    disable: bool = False,
) -> DataFrame:
    if not read_kwds:
        read_kwds = {}

    if not write_kwds:
        write_kwds = {}

    def _inner(f):
        @functools.wraps(f)
        def _wrapper(*args, **kwds):
            cache_file = os.path.join(cache_dir, file)
            ext = os.path.splitext(file)[1]
            io = _IO_HELPERS.get(ext)
            if not io:
                raise ValueError(
                    f"Unsupported file types: {ext}"
                    f", supported file types are: {', '.join(_IO_HELPERS)}"
                )

            if not disable and os.path.exists(cache_file):
                df = io.reader(cache_file, **read_kwds)
                logger.debug("Read dataframe cache from: %s", cache_file)
            else:
                os.makedirs(cache_dir, exist_ok=True)
                df = f(*args, **kwds)
                io.writer(df, cache_file, **write_kwds)
                logger.debug("Saved dataframe cache to: %s", cache_file)

            return df

        return _wrapper

    return _inner