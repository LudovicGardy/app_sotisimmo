def calculate_median_difference(summarized_df_pandas, selected_department, normalize_by_area, property_type):

    # Filter the summarized data for the given department
    dept_data = summarized_df_pandas[summarized_df_pandas['code_departement'] == selected_department]
    column_to_use = 'Median Value SQM' if normalize_by_area else 'Median Value'
    
    type_data = dept_data[dept_data['type_local'] == property_type]
    type_data = type_data.sort_values(by="Year")

    # Calculate the annual differences
    type_data['annual_diff'] = type_data[column_to_use].diff()
    
    # Calculate the average annual difference (excluding NaN values)
    annual_average_diff = type_data['annual_diff'].dropna().mean()
    
    # Calculate percentage difference between 2018 and 2022
    try:
        value_2018 = type_data[type_data['Year'] == 2018][column_to_use].values[0]
        value_2022 = type_data[type_data['Year'] == 2023][column_to_use].values[0]
        percentage_diff = ((value_2022 - value_2018) / value_2018) * 100
    except IndexError:
        percentage_diff = "NA"
    

    return(annual_average_diff, percentage_diff)