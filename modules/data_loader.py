import pandas as pd
import requests
import streamlit as st
from io import BytesIO
import pymssql

from .config import data_URL, azure_credentials

@st.cache_data
def fetch_summarized_data():
    print("Fetching summarized data...")

    ### Download data summarized from AWS S3
    url = data_URL().get('summarized_data_url')
    response = requests.get(url)

    ### Store data in a buffer
    buffer = BytesIO(response.content)

    ### Load data into a Pandas dataframe
    summarized_df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                            dtype={'code_postal': str})
    
    return summarized_df_pandas


@st.cache_data
def fetch_data_AzureSQL(selected_dept):

    print("Fetching data from Azure SQL... Year: 2024, Department: {}".format(selected_dept))

    ### Fetch only when user changes the year
    cred_dict = azure_credentials()

    sql_query = f"""
        SELECT DISTINCT
            type_local,
            valeur_fonciere,
            code_postal,
            surface,
            longitude,
            latitude
        FROM
            {cred_dict['AZURE_TABLE']}
        WHERE
            code_departement = '{selected_dept}' AND
            type_local IS NOT NULL
        """
    
    try:
        # Establish a connection to the database
        conn = pymssql.connect(server=cred_dict['AZURE_SERVER'], user=cred_dict['AZURE_UID'], password=cred_dict['AZURE_PWD'], database=cred_dict['AZURE_DATABASE'])
        
        # Execute the query and store the result in a pandas DataFrame
        df = pd.read_sql(sql_query, conn)
        df.rename(columns={'surface': 'surface_reelle_bati'}, inplace=True)

        # # Close the connection
        conn.close()
        
        return df

    except Exception as e:
        if df is None:
            st.sidebar.error("Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(selected_dept, selected_year))
            st.session_state.data_load_error = True
        # st.warning(e)
        st.warning("Les données n'ont pas pu être chargées.")
        print(e)


def update_data_AzureSQL():
    ### Update request when user changes the departement
    pass

### Load data 
@st.cache_data
def fetch_data_gouv(selected_dept, selected_year):
    '''
    Load data from the French open data portal.
    @st.cache_data is used to cache the data, so that it is not reloaded every time the user changes a parameter.

    Data are organized as follows:
    - 2018
     - 01
        - appartement
        - maison
        - ...
     - 02
     - 03
     - ...

    - 2019
     - 01
        - appartement
        - maison
        - ...
     - 02
     - 03
     - ...

    ...

    So this function should be called each time the user selects a new department or a new year.
    '''

    print("Fetching data from the French open data portal... Year: {}, Department: {}".format(selected_year, selected_dept))
    df_pandas = None  # Initialisez df_pandas à None ou pd.DataFrame()

    # Data from government are available only for the years 2018-2022
    try:
        if int(selected_year) < 2024:
            ### Download data from the French open data portal
            url = f'{data_URL().get("data_gouv")}/{selected_year}/departements/{selected_dept}.csv.gz'
            response = requests.get(url)

            ### Store data in a buffer
            buffer = BytesIO(response.content)

            ### Load data into a Pandas dataframe
            df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                    usecols=['type_local', 'valeur_fonciere', 'code_postal', 'surface_reelle_bati', 'longitude', 'latitude'],
                                    dtype={'code_postal': str})
        else:
            usecols = ['type_local', 'valeur_fonciere', 'code_postal', 'surface_reelle_bati']
            df_pandas = fetch_data_AzureSQL(usecols)

        ### Remove rows with missing values
        df_pandas.dropna(inplace=True)

        ### Remove duplicates based on the columns 'valeur_fonciere', 'longitude', and 'latitude'
        df_pandas.drop_duplicates(subset=['valeur_fonciere', 'longitude', 'latitude'], inplace=True, keep='last')

        ### Sort by postal code
        df_pandas = df_pandas.sort_values('code_postal')

        ### Add leading zeros to postal code
        df_pandas['code_postal'] = df_pandas['code_postal'].astype(float).astype(int).astype(str).str.zfill(5)

    except Exception as e:
        if df_pandas is None:
            st.sidebar.error("Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(selected_dept, selected_year))
            st.session_state.data_load_error = True
        # st.warning(e)
        st.warning("Les données n'ont pas pu être chargées.")
        print(e)

    return df_pandas
