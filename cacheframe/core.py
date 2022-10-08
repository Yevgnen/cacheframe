# -*- coding: utf-8 -*-

import datetime
import functools
import logging
import os
from dataclasses import dataclass
from typing import Callable, Mapping, Optional, Union

import pandas as pd
from pandas import DataFrame

logger = logging.getLogger(__name__)

OriginalFun = Callable[[Any, ...], DataFrame]
DecoratedFun = Callable[[Any, ...], DataFrame]


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
    ttl: Optional[int] = None,
    disable: bool = False,
) -> Callable[[OriginalFun], DecoratedFun]:
    """Decorator to help cache dataframe return value.

    Args:
        cache_dir (Union[str, os.PathLike]): directory to place cache
            files (default: .cache)

        file (str): cache file name, support file types are: .csv,
            .xlxs, .pickle, .json, .parquet and .feather
            (default: dataframe.parquet)

        read_kwds (Optional[Mapping]): optional keyword arguments passed
            to readers (pandas.to_*) when reading cache (default: None)

        write_kwds (Optional[Mapping]): optional keyword arguments
            passed to writers (pandas.read_*) when writing cache
            (default: None)

        ttl (Optional[int]): optional TTL value to invalid cache
            (default: None)

        disable (bool): boolean indicator to enable or disable cache
            (default: False)

    Returns:
        Callable[[OriginalFun], DecoratedFun]: Decorated function.
    """
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

            existed = os.path.exists(cache_file)
            expired = (
                existed
                and ttl is not None
                and datetime.datetime.now().timestamp() - os.path.getctime(cache_file)
                > ttl
            )
            if not disable and existed and not expired:
                df = io.reader(cache_file, **read_kwds)
                logger.debug("Read dataframe cache from: %s", cache_file)
            else:
                df = f(*args, **kwds)
                if not isinstance(df, DataFrame):
                    raise ValueError(
                        "Wrapped function should return single DataFrame"
                        f", got: {df.__class__.__name__}"
                    )

                os.makedirs(cache_dir, exist_ok=True)
                io.writer(df, cache_file, **write_kwds)
                logger.debug(
                    "%s dataframe cache to: %s",
                    "Updated" if expired else "Saved",
                    cache_file,
                )

            return df

        return _wrapper

    return _inner
