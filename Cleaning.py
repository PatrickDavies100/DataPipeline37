import math
from collections import defaultdict
import pandas as pd
from PySide6.QtCore import QObject, Signal
from pandas import value_counts

import ProcessesController

# Set pandas display options
pd.set_option('display.max_rows', 200)  # Show more rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Set the display width
pd.set_option('display.max_colwidth', None)  # Show full column content


def get_metadata(df: pd.DataFrame) -> str:
    """Return basic metadata for a dataframe as a string."""
    result = ''
    # Get number of columns and records
    shape = df.shape
    result += f'Column count = {shape[1]} \n'
    result += f'Total records = {shape[0]} \n'

    # Get datatypes of the columns
    return result


def category_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Filters a dataframe by category with optional extra features
    """


def find_string_instances(ser: pd.Series, input_string: str, case_sensitive: bool
                          = True) -> dict:
    """Finds instances of a substring in a series.

    This function returns a dict where the key is the row in the Series and the value is a list of
    the locations where the substring occurs.
    """
    positives = {}
    if ser.dtype == object:
        for ser_index, value in ser.items():
            if case_sensitive is False:
                value = value.lower()
                input_string = input_string.lower()
            instances = value.count(input_string)
            search_point = 0
            locations = []
            while instances > 0:
                search_point = value.index(input_string, search_point) + 1
                locations.append(search_point - 1)
                instances -= 1
                if instances == 0:
                    positives.update({ser_index: locations})
    else:
        print ('wrong datatype')
        print (ser.dtype)
    return positives


def find_num_instances(s: pd.Series) -> pd.Series:
    """Finds instances of a numeric value in a series.
    """
    if s.dtype == int:
        print ('nuggies')
    elif s.dtype == float:
        print ('buggies')
    else:
        print ('error')


def string_replace(s: pd.Series, input_string: str, new_string: str, count: int = 0) \
        -> pd.Series:
    """Replaces a substring in a series with a new string.

    Positional args:
    input_string: the string to be replaced
    new_string: the string that will replace it
    count: how many replacements to make per row
    """
    replace_dict = find_string_instances(s, input_string)
    #in replace_dict, row is where we find the replacements, location is the index to replace

    new_series = []

    for i in range(len(s)):
        if count == 0:
            new_series.append(s[i].replace(input_string, new_string))
        else:
            new_series.append(s[i].replace(input_string, new_string, count))

    new_series = pd.Series(new_series)
    return new_series


def unique_value_count(s: pd.Series) -> tuple:
    """Returns data about unique values in a series

        Must have a series as the first argument. The second argument is how many rows to check,
        if no argument is given then the whole series is checked.

        Values are returned as a tuple:
        The total number of distinct values as an integer
        The total of null values as an integer
        The ratio of distinct values to total records as a float
        """
    # Check datatype for series
    print(s.dtype)
    series_dt = str(s.dtype)
    if series_dt == 'float64' or series_dt == 'int64':
        result = numeric_unique_value_count(s)
    else:
        result = (0, 0, 0)
        print('Error!')
    return result


def numeric_unique_value_count(s: pd.Series, check_rows: int = 0) -> tuple:
    """Counts unique values in a series of numeric data."""
    # Set defaults
    null_counter = 0
    if check_rows == 0:
        check_rows = len(s)
    s = s.head(check_rows)

    # Function for defaultdict
    def def_value():
        return 0

    # Get unique value count for data including nulls
    value_freq_dict = defaultdict(def_value)
    for i in range(check_rows):
        if not math.isnan(s.iloc[i]):
            value_freq_dict[s.iloc[i]] += 1
            print(type(s.iloc[i]))
        else:
            null_counter += 1
            print('Null value found')
    unique_count = len(value_freq_dict)
    if null_counter > 0:
        unique_count += 1

    # Get ratio
    ratio = unique_count / len(s)

    return unique_count, null_counter, ratio


def float_to_int(ser: pd.Series, nulls: int = 0, rounding: bool = False,
                 rounding_point: float = 0.5) -> pd.Series:
    """Converts a series from float values to int.

    Must have a series as the first argument.

    Nulls - If a value is null, this value will replace it. Defaults to zero.
    Rounding - can accept 'up', 'down' or 'off' If no argument is given, it will default
    to 'off' which means that all values round down.
    """
    # Error handling - datatype is not expected, column not found
    # Needs to check for column as string or int
    ser = ser.fillna(nulls)
    if rounding:
        ser = rounder(ser, rounding_point)
    ser = ser.astype(int)
    ProcessesController.add_process(('Convert float to int',
                                     ser))
    return ser


def series_replace(df: pd.DataFrame, column: int, ser: pd.Series) -> pd.DataFrame:
    """Replaces a series in a dataframe using the column index
    """
    if len(df.iloc[:, column]) != len(ser):
        return df
    col_label = df.keys()[column]
    ser.index = df.iloc[:, column].index
    df = df.drop(df.columns[column], axis=1)
    df.insert(column, col_label, ser)
    return df


def rounder(ser: pd.Series, rounding_point: float) -> pd.Series:
    """Rounds float values in a series"""
    for i in range(len(ser)):
        value = (ser.iloc[i])
        if value / 1.0 != 0:
            remainder = (value % 1.0)
            if remainder <= rounding_point:
                value -= remainder
            else:
                value += (1 - remainder)
            ser.iloc[i] = value
    return ser


def outliers(ser: pd.Series, method: str = '') -> dict:
    """Returns values at given quartiles

    This method is useless because of in-built quantile
    """
    low, high = median_split(ser)
    q1 = low.median()
    q3 = high.median()
    print('q1 is ' + str(q1))
    print('q3 is ' + str(q3))
    outlying_values = dict()
    for index, value in ser.items():
        if value < q1 or value > q3:
            outlying_values.update({index: value})
    return outlying_values


def median_split(ser: pd.Series) -> tuple:
    low = dict()
    high = dict()
    for index, value in ser.items():
        if value < ser.median():
            low.update({index: value})
        else:
            high.update({index: value})
    s_low = pd.Series(data=low)
    s_high = pd.Series(data=high)

    return s_low, s_high


def test_dataframe_constructor() -> pd.DataFrame:
    print('Generating dataframe of test data')
    d = {'col1': [1, 3, 3], 'col2': [4, None, 6], 'col3': [8.19
        , None, 8.5], 'col4': [1.2, None, None]}
    df = pd.DataFrame(data=d)
    return df


def test_series_constructor() -> pd.Series:
    print('Generating Test Series')
    d = {0: 1.2, 1: 2.9, 2: 3.5, 3: 4.3, 4: 5.7, 5: 6.1}
    ser = pd.Series(data=d, index=[0, 1, 2, 3, 4, 5])
    return ser


class StatusEmitter(QObject):
    """Sends signal to front end for testing"""
    send_string = Signal(str)
    send_series = Signal(pd.Series)
    send_df = Signal(pd.DataFrame)

    def run_test_function_2(self):
        test_series = test_series_constructor()
        self.send_series.emit(test_series)

    def dataframe_sender(self):
        test_df = test_dataframe_constructor()
        self.send_df.emit(test_df)