import pandas as pd
import requests
import streamlit as st
import json
import os
from io import BytesIO
from google.cloud import bigquery
from google.oauth2 import service_account

from .config import data_URL, load_configurations

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
def fetch_data_BigQuery(_cred_dict, selected_dept):
    print(f"Fetching data from BigQuery... Year: 2024, Department: {selected_dept}")

    env_variables = load_configurations()

    # Créer un fichier JSON temporaire pour stocker les credentials et les envoyer à BigQuery
    credentials_path = 'temp_credentials.json'
    with open(credentials_path, 'w') as credentials_file:
        json.dump(_cred_dict, credentials_file)

    # Utiliser le fichier JSON temporaire pour créer les credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    client = bigquery.Client(credentials=credentials, project=_cred_dict["project_id"])

    # Supprimer le fichier temporaire après utilisation
    os.remove(credentials_path)

    sql_query = f"""
        SELECT DISTINCT
            type_local,
            valeur_fonciere,
            code_postal,
            surface,
            longitude,
            latitude
        FROM
            `{env_variables.get('BIGQUERY_PROJECT_ID')}.{env_variables.get('BIGQUERY_DATASET_ID')}.{env_variables.get('BIGQUERY_TABLE')}`
        WHERE
            code_departement = '{selected_dept}' AND
            type_local IS NOT NULL
    """

    try:
        # Exécutez la requête et stockez le résultat dans un DataFrame Pandas
        df = client.query(sql_query).to_dataframe()
        df.rename(columns={'surface': 'surface_reelle_bati'}, inplace=True)
        return df

    except Exception as e:
        st.warning("Les données n'ont pas pu être chargées depuis BigQuery.")
        print(e)

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
        ### Download data from the French open data portal
        url = f'{data_URL().get("data_gouv")}/{selected_year}/departements/{selected_dept}.csv.gz'
        response = requests.get(url)

        ### Store data in a buffer
        buffer = BytesIO(response.content)

        ### Load data into a Pandas dataframe
        df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
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
        st.warning("Les données n'ont pas pu être chargées.")
        print(e)

    return df_pandas
