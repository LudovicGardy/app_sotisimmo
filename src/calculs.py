from typing import Tuple

import pandas as pd


def calculate_median_difference(
    properties_summarized: pd.DataFrame,
    selected_department: str,
    normalize_by_area: bool,
    local_type: str,
    to_year: int,
) -> Tuple[float, float]:
    to_year = int(to_year)
    from_year = to_year - 1

    # Filter the summarized data for the given department
    properties_summarized = properties_summarized[properties_summarized["code_departement"] == selected_department]
    properties_summarized = properties_summarized[properties_summarized["Year"] <= to_year]
    column_to_use = "Median Value SQM" if normalize_by_area else "Median Value"

    type_data = properties_summarized[properties_summarized["type_local"] == local_type]
    type_data = type_data.sort_values(by="Year")

    # Calculate the annual differences
    type_data["annual_diff"] = type_data[column_to_use].diff()

    # Calculate the average annual difference (excluding NaN values)
    annual_average_diff = type_data["annual_diff"].dropna().mean()

    # Calculate percentage difference between 2018 and selected_year
    try:
        value_2018 = type_data[type_data["Year"] == from_year][column_to_use].values[0]
        value_selected_year = type_data[type_data["Year"] == to_year][column_to_use].values[0]
        percentage_diff = ((value_selected_year - value_2018) / value_2018) * 100
    except IndexError:
        percentage_diff = 0.0

    return (annual_average_diff, percentage_diff)
