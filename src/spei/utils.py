from pandas import Series, DataFrame


def check_series(series):
    """Check if provided time series is of type pandas.Series

    Parameters
    ----------
    series : any
        Time series of any kind

    Raises
    ------
    TypeError
        If series is not a pandas.Series

    """
    if not isinstance(series, Series):
        if isinstance(series, DataFrame):
            raise TypeError(
                f'Please convert pandas.DataFrame to a pandas.Series using .squeeze()')
        else:
            raise TypeError(
                f'Please provide a Pandas Series instead of {type(series)}')
