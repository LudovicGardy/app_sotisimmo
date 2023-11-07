import pandas as pd
import requests
import streamlit as st
from io import BytesIO

from .config import data_URL

def load_summarized_data():

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
def fetch_data_AzureSQL(selected_dept, selected_year):
    ### Remember to fetch data only once
    pass

### Load data 
@st.cache_data
def fetch_data_gouv(selected_dept, selected_year):
    '''
    Load data from the French open data portal.
    @st.cache_data is used to cache the data, so that it is not reloaded every time the user changes a parameter.
    '''
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
            csv_path = f'{data_URL().get("2024_merged")}/{selected_dept}.csv.gz'
            df_pandas = pd.read_csv(csv_path, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                        usecols=['type_local', 'valeur_fonciere', 'code_postal', 'surface_reelle_bati', 'longitude', 'latitude'],
                                        dtype={'code_postal': str})

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
        st.warning('Oups, un petit bug ici.')
        print(e)

    return df_pandas