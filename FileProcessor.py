import pandas as pd
from datetime import datetime
from PySide6.QtCore import QObject, Signal

#File Process Key

import ProcessesController


class CurrentDataFrame:
    """The dataframe that is active"""
    _instance = None
    _dataframe = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurrentDataFrame, cls).__new__(cls)
            cls._dataframe = pd.DataFrame()
        return cls._instance

    def get_dataframe(self):
        return self._dataframe

    def update_dataframe(self, new_df):
        self._dataframe = new_df

class TempDataFrame:
    """A temporary dataframe that the user can review before changing Current Dataframe

    This should be a sample of limited size to improve performance."""
    _instance = None
    _dataframe = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TempDataFrame, cls).__new__(cls)
            cls._dataframe = pd.DataFrame()
        return cls._instance

    def get_dataframe(self):
        return self._dataframe

    def update_dataframe(self, new_df):
        self._dataframe = new_df

def read_file(filename: str) -> pd.DataFrame | None:
    """Reads supported filetypes and outputs them as a Dataframe

    Supported filetypes: CSV, JSON
    """

    fileend = filename[-3:]

    if fileend.__eq__('csv'):
        print(f'Reading CSV file "{filename}" ')
        df = read_csv(filename)
    elif filename[0].__eq__('{') and filename[-1].__eq__('}'):
        print(f'Reading JSON file "{filename}" ')
        df = read_json(filename)
    else:
        return None
    return df


def read_csv(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df


def read_json(filename: str) -> pd.DataFrame:
    df = pd.read_json(filename)
    return df


def read_excel(filename: str) -> pd.DataFrame:
    df = pd.read_excel(filename)
    return df


def test_dataframe_constructor() -> pd.DataFrame:
    print('Generating dataframe of test data in FileProcessor module')
    d = {'col1': ['bbaba', 'aa', 'da', 'c', 'a', 'a', 'a', 'a', 'a', 'a'],
         'col2': [4, None, 6, 1, 3, 3, 4, None, 6, 1],
         'col3': [8.19, None, 8.5, 4, None, 6, 1, 3, 3, 10],
         'col4': [1.2, None, None, 4, None, 6, 1, 3, 3, 1]}
    df = pd.DataFrame(data=d)
    c = TempDataFrame()
    c.update_dataframe(new_df=df)
    ProcessesController.add_process(('Generate test dataframe',
                                     -1))
    return c.get_dataframe()


class DataEmitter(QObject):
    """Sends data to the front end"""
    send_string = Signal(str)
    send_series = Signal(pd.Series)
    send_df = Signal(pd.DataFrame)

    def dataframe_sender(self):
        d = test_dataframe_constructor()
        self.send_df.emit(d)



