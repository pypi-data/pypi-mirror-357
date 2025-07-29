import pandas as pd


__all__ = [
    "check_columns", 
    "nan_count"
]


def check_columns(df: pd.DataFrame, allowed_checks: dict) -> pd.DataFrame:
    """
    Check DataFrame columns for invalid values based on allowed values or conditions.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to check.
    allowed_checks : dict
        Dictionary specifying validation rules per column:
        - Key: column name (str)
        - Value: either a list of allowed values or a callable condition (e.g., a lambda function).

    Returns
    -------
    pandas.DataFrame
        A DataFrame summarizing invalid values with columns:
        - 'Rows': Row numbers (1-based) where invalid values occur or empty string if column missing.
        - 'Column': Name of the column with invalid values.
        - 'Invalid Value': The invalid value found or 'Column not found' if column is missing.
    """

    rows = []

    for col, allowed in allowed_checks.items():
        if col not in df.columns:
            rows.append({
                'Rows': '',
                'Column': col,
                'Invalid Value': 'Column not found'
            })
            continue

        invalid_indices = []

        if callable(allowed):
            mask_invalid = ~df[col].apply(allowed)
            invalid_values = df.loc[mask_invalid, col].unique()
        else:
            mask_invalid = ~df[col].isin(allowed) & df[col].notna()
            invalid_values = df.loc[mask_invalid, col].unique()

        for val in invalid_values:
            indices = df.index[df[col] == val].tolist()
            rows_str = ",".join(str(idx + 1) for idx in indices)
            rows.append({'Rows': rows_str, 'Column': col, 'Invalid Value': val})

    return pd.DataFrame(rows, columns=['Rows', 'Column', 'Invalid Value'])


def nan_count(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the count and percentage of NaN values for each column in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to analyze.

    Returns
    -------
    pandas.DataFrame
        A summary DataFrame with columns:
        - "Column": Name of each column in the input DataFrame.
        - "NaN count": Number of NaN values in the column.
        - "Percent": Percentage of NaN values relative to the total number of rows, rounded to 2 decimals.
    """

    total_rows = len(df)
    summary = []
    for column in df.columns:
        nan_count = df[column].isna().sum()
        nan_percent = (nan_count / total_rows) * 100
        summary.append({
            "Column": column,
            "NaN count": nan_count,
            "Percent": round(nan_percent, 2)
        })
    return pd.DataFrame(summary)