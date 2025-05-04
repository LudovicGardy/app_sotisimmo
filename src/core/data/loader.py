"""
Data loading module for the Sotis Immobilier application.
This module handles all data loading operations from various sources.
"""

from io import BytesIO
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from src.config.config import get_data_config


class DataLoader:
    """Class responsible for loading data from various sources."""

    def __init__(self):
        """Initialize the DataLoader with configuration settings."""
        self.config = get_data_config()

    @st.cache_data
    def fetch_summarized_data(self) -> pd.DataFrame:
        """
        Fetch the summarized property data from AWS S3.
        
        Returns:
            pd.DataFrame: DataFrame containing the summarized property data.
        """
        print("Fetching summarized data...")

        try:
            response = requests.get(self.config.summarized_data_url)
            response.raise_for_status()
            
            buffer = BytesIO(response.content)
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
            
        except requests.RequestException as e:
            st.error(f"Error fetching summarized data: {str(e)}")
            raise

    @staticmethod
    @st.cache_data
    def fetch_data_gouv(selected_dept: str, selected_year: int) -> Optional[pd.DataFrame]:
        """
        Load data from the French open data portal.
        
        Args:
            selected_dept (str): The selected department code.
            selected_year (int): The selected year.
            
        Returns:
            Optional[pd.DataFrame]: DataFrame containing the property data or None if loading fails.
            
        Note:
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
        """
        print(f"Fetching data from the French open data portal... Year: {selected_year}, Department: {selected_dept}")

        try:
            config = get_data_config()
            url = f"{config.datagouv_source_url}/{selected_year}/departements/{selected_dept}.csv.gz"
            response = requests.get(url)
            response.raise_for_status()

            buffer = BytesIO(response.content)
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
                    "nom_commune",
                    "surface_reelle_bati",
                    "longitude",
                    "latitude",
                ],
                dtype={"code_postal": str},
            )

            # Data cleaning
            properties_input.dropna(inplace=True)
            properties_input.drop_duplicates(
                subset=["valeur_fonciere", "longitude", "latitude"],
                inplace=True,
                keep="last",
            )
            properties_input.sort_values("code_postal", inplace=True)
            
            # Format postal code
            properties_input["code_postal"] = (
                properties_input["code_postal"]
                .astype(float)
                .astype(int)
                .astype(str)
                .str.zfill(5)
            )

            return properties_input

        except requests.RequestException as e:
            st.sidebar.error(
                f"Pas d'information disponible pour le département {selected_dept} en {selected_year}. "
                "Sélectionnez une autre configuration."
            )
            st.session_state.data_load_error = True
            st.warning("Les données n'ont pas pu être chargées.")
            print(f"Error fetching data: {str(e)}")
            return None 