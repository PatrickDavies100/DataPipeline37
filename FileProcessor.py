import json
import pandas as pd
from pandas import DataFrame


def read_file(filename: str) -> DataFrame | None:
    """Reads supported filetypes and outputs them as a Dataframe

    Supported filetypes: CSV, JSON
    """

    fileEnd = filename[-3:]

    if fileEnd.__eq__('csv'):
        print(f'Reading CSV file "{filename}" ')
        df = read_CSV(filename)
    elif filename[0].__eq__('{') and filename[-1].__eq__('}'):
        print(f'Reading JSON file "{filename}" ')
        df = read_JSON(filename)
    else:
        return None
    return df


def read_CSV(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df


def read_JSON(filename: str) -> pd.DataFrame:
    df = pd.read_json(filename)
    return df


def read_excel(filename: str) -> pd.DataFrame:
    df = pd.read_excel(filename)
    return df
