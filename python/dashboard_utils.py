"""Small, testable helpers used by the Streamlit dashboard."""

import pandas as pd


def filter_by_date_selection(data: pd.DataFrame, selection) -> pd.DataFrame:
    """Filter rows for Streamlit date_input's single-date or range selection.

    Streamlit can return a single date when one day is selected, a two-item
    tuple for a range, and an empty tuple when the selection is cleared.
    """
    if isinstance(selection, (tuple, list)):
        if not selection:
            return data.copy()
        if len(selection) == 1:
            start_date = end_date = selection[0]
        elif len(selection) == 2:
            start_date, end_date = selection
        else:
            raise ValueError("Date selection must contain one date or a start/end pair.")
    elif selection is None:
        return data.copy()
    else:
        start_date = end_date = selection

    if start_date is None or end_date is None:
        return data.copy()

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    date_values = pd.to_datetime(data["Date"], errors="coerce").dt.date
    return data.loc[date_values.between(start_date, end_date)].copy()
