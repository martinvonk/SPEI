from pandas import Series, DataFrame


def check_series(series):

    if not isinstance(series, Series):
        if isinstance(series, DataFrame):
            raise TypeError(
                f'Please convert pandas DataFrame to a Series using .squeeze()')
        else:
            raise TypeError(
                f'Please provide a Pandas Series instead of {type(series)}')
