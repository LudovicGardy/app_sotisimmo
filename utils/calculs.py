def calculate_median_difference(summarized_df_pandas, selected_department, normalize_by_area, local_type, to_year):

    to_year = int(to_year)
    from_year = to_year - 1

    # Filter the summarized data for the given department
    summarized_df_pandas = summarized_df_pandas[summarized_df_pandas['code_departement'] == selected_department]
    summarized_df_pandas = summarized_df_pandas[summarized_df_pandas['Year'] <= to_year]
    column_to_use = 'Median Value SQM' if normalize_by_area else 'Median Value'
    
    type_data = summarized_df_pandas[summarized_df_pandas['type_local'] == local_type]
    type_data = type_data.sort_values(by="Year")

    # Calculate the annual differences
    type_data['annual_diff'] = type_data[column_to_use].diff()
    
    # Calculate the average annual difference (excluding NaN values)
    annual_average_diff = type_data['annual_diff'].dropna().mean()
    
    # Calculate percentage difference between 2018 and selected_year
    try:
        value_2018 = type_data[type_data['Year'] == from_year][column_to_use].values[0]
        value_selected_year = type_data[type_data['Year'] == to_year][column_to_use].values[0]
        percentage_diff = ((value_selected_year - value_2018) / value_2018) * 100
    except IndexError:
        percentage_diff = "NA"
    

    return(annual_average_diff, percentage_diff)