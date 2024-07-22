import json
import os
from io import BytesIO

import pandas as pd
import requests
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

from .config import data_URL, load_configurations


@st.cache_data
def fetch_summarized_data() -> pd.DataFrame:
    print("Fetching summarized data...")

    ### Download data summarized from AWS S3
    url = str(data_URL().get("summarized_data_url"))
    response = requests.get(url)

    ### Store data in a buffer
    buffer = BytesIO(response.content)

    ### Load data into a Pandas dataframe
    properties_summarized = pd.read_csv(
        buffer,
        compression="gzip",
        header=0,
        sep=",",
        quotechar='"',
        low_memory=False,
        dtype={"code_postal": str},
    )

    return properties_summarized


@st.cache_data
def fetch_data_BigQuery(_cred_dict: dict[str, str], selected_dept: str) -> pd.DataFrame:
    print(f"Fetching data from BigQuery... Year: 2024, Department: {selected_dept}")

    env_variables = load_configurations()

    # Créer un fichier JSON temporaire pour stocker les credentials et les envoyer à BigQuery
    credentials_path = "temp_credentials.json"
    with open(credentials_path, "w") as credentials_file:
        json.dump(_cred_dict, credentials_file)

    # Utiliser le fichier JSON temporaire pour créer les credentials
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )
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
        df.rename(columns={"surface": "surface_reelle_bati"}, inplace=True)
        return df

    except Exception as e:
        st.warning("Les données n'ont pas pu être chargées depuis BigQuery.")
        print(e)


### Load data
@st.cache_data
def fetch_data_gouv(selected_dept: str, selected_year: int) -> pd.DataFrame:
    """
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
    """

    print(
        "Fetching data from the French open data portal... Year: {}, Department: {}".format(
            selected_year, selected_dept
        )
    )
    properties_input = None  # Initialisez properties_input à None ou pd.DataFrame()

    # Data from government are available only for the years 2018-2022
    try:
        ### Download data from the French open data portal
        url = f'{data_URL().get("datagouv_source_URL")}/{selected_year}/departements/{selected_dept}.csv.gz'
        response = requests.get(url)

        ### Store data in a buffer
        buffer = BytesIO(response.content)

        ### Load data into a Pandas dataframe
        properties_input = pd.read_csv(
            buffer,
            compression="gzip",
            header=0,
            sep=",",
            quotechar='"',
            low_memory=False,
            usecols=[
                "type_local",
                "valeur_fonciere",
                "code_postal",
                "surface_reelle_bati",
                "longitude",
                "latitude",
            ],
            dtype={"code_postal": str},
        )

        ### Remove rows with missing values
        properties_input.dropna(inplace=True)

        ### Remove duplicates based on the columns 'valeur_fonciere', 'longitude', and 'latitude'
        properties_input.drop_duplicates(
            subset=["valeur_fonciere", "longitude", "latitude"],
            inplace=True,
            keep="last",
        )

        ### Sort by postal code
        properties_input = properties_input.sort_values("code_postal")

        ### Add leading zeros to postal code
        properties_input["code_postal"] = (
            properties_input["code_postal"]
            .astype(float)
            .astype(int)
            .astype(str)
            .str.zfill(5)
        )

    except Exception as e:
        if properties_input is None:
            st.sidebar.error(
                "Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(
                    selected_dept, selected_year
                )
            )
            st.session_state.data_load_error = True
        # st.warning(e)
        st.warning("Les données n'ont pas pu être chargées.")
        print(e)

    return properties_input
