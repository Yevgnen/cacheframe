# -*- coding: utf-8 -*-

import time

import pandas as pd
from pandas import DataFrame

import cacheframe
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
