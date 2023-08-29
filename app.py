import streamlit as st
import requests
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
import matplotlib.cm as cm
import streamlit.components.v1 as components
from gzip import BadGzipFile
import platform
import os
from tempfile import NamedTemporaryFile
import json

### Analytics data will be stored in a Google Cloud Firestore database
import streamlit_analytics
from google.cloud import firestore

from dotenv import load_dotenv, dotenv_values

try:
    # Chargez les variables d'environnement à partir du fichier .env
    config = dotenv_values(".env")
    cred_dict = {
    "type": "service_account",
    "project_id": config['PROJECT_ID'],
    "private_key_id": config['PRIVATE_KEY_ID'],
    "private_key": f"-----BEGIN PRIVATE KEY-----\n{config['PRIVATE_KEY']}\nQRvUMBhovN3NVKFCWGI242MTctN8p5VTnAgbMWEaoCuajuZAiqZIr0ekSYMrPY9U\nK8sQF259Mm10v5AMCyNhFkfB3Hb9Um18kxTlzh8zgHilznxTCY62/fgvcSGE2mPM\nPd5yHtXGWlmnbRKQrT1v0uTlTOSentJRedfa5qDbe4mOyWAVUlSnB39xG/3bxen5\nSWBj2x2ReeK2YnSL+xHkyYk9sDlzgw4ODcdPpM2gHprt9dqdkKxT+y0AiJJz/Hu/\nw53kKPBkp+Cf/4XJtPOafe4ncydD5Tj1XS9rKGvyOgOMV3UrDjh0To90FcGJNCL5\nxXyn94onAgMBAAECggEABlYbkhpz4sKHIcTWIAfPkHqNqqr90NCajInhMDPmeDP3\nNJI+MaVJzTLFGduBXfmd8tUto8ILE04MHyMyy9MluZ9zDTLfiUN/h2zXL+RlG/tt\nUW6QoIPFmVh7Z1PBS2c1fb4nQffVBEPxbh24cPBdp4LlaTnpxxWzUuCmI3rHqXHm\nVOoW66TTdn2fk8hhjJaYzCulL6/pOuRMMWCu3xvt+VeVHlpdq3J6CAxImAvHedMI\nxzfXd/Lcialv0geN1TI6EqUfDD7D1ZZqsrksNZM1inmUwK48LrSSYZjkm51voYzf\nFD7y5qKU8hq/FAV7flbh2wuAtSLubETGRKHLjpXIeQKBgQD7zEMNLDSZJymextbt\nUrk6Jh1v73kFFXDJv/CTEybO+3BTIBcJVjzXAG0mF7NERlUy6jiHee9aISXoTm8R\necNo+n1AngBz7bCTWRhT/eblSLVSMN2hwwgdQuqWpJZWFO7ZtR349K/VX0zBFPtF\n98Asgnmqg8X9X4s7JSzle1gWgwKBgQDvNF1Aft5AqP6CAF/oP7+g/eBvnxDtDg1R\nS6Pl24nxSMtFVa4wfq2gM10E98971Vq7VsxNWqo2W3CT85jKe0D3zRAGlZ0jjMl5\nIhUt8V2Vq6q6MvEIAVgesZtvOXb2K9f3h1BOdIP2WPRXGJDnuGY9j0u4UWW7SUAb\naBhYdfcMjQKBgC8lZNyfjU2r3ogjNPUEyzfPES33SdKg3Bh6fuIa8OZKgBKgbI/L\n/OJI6yb5wxAilytMXb9IHn/iuwVPQk6kXOlYFYG20+Dg/XHpebuoS8Zcoc685ZK3\nQNqxv9jrAlcl3j8XQYBu2El8aZOxiQblx67N01gRCk5RyHEPmeNx/+FfAoGARfYq\n0BJLLt4+kgdKBcOfaJbYbc04Rh02B/D3nuL3FXsU+NJ2f/iND632Jt3T8YQVZXWd\ni4JZBkz4QE2fApnKBrATX9mifCNRSfyN9UIC/SOYa506ofzCqTeJHp7QDHAGWn9Z\nHZk2f3bFADRPLXbhcF/Y5a/o8T4bYeiwNi9KcoECgYBGJ5NmQVy6ts19DpyWzK2+\nK8mG+vCx1rLfhwNW8ssrQsa+k9CE+krj/LflxfkHzQcOVoTgRxbHxT/TgBYCuoyE\nhnQb2L0bA/tayaMG2mz6rfBt6spliAaLl+4bvu6BWP4KY0jqg+mUsyrqumHNVgSp\nqqoHxy8uVFxNcMOw8AStmg==\n-----END PRIVATE KEY-----\n",
    "client_email": config['CLIENT_EMAIL'],
    "client_id": config['CLIENT_ID'],
    "auth_uri": config['AUTH_URI'],
    "token_uri": config['TOKEN_URI'],
    "auth_provider_x509_cert_url": config['AUTH_PROVIDER_X509_CERT_URL'],
    "client_x509_cert_url": config['CLIENT_X509_CERT_URL']
    }
except Exception as e:
    # Récupérez les valeurs à partir des variables d'environnement
    print("No file .env was found :", str(e))
    print("Searching in OS environment variables...")
    # load_dotenv()
    cred_dict = {
        "type": "service_account",
        "project_id": os.environ.get('PROJECT_ID'),
        "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
        "private_key": f"-----BEGIN PRIVATE KEY-----\n{os.environ.get('PRIVATE_KEY')}\nQRvUMBhovN3NVKFCWGI242MTctN8p5VTnAgbMWEaoCuajuZAiqZIr0ekSYMrPY9U\nK8sQF259Mm10v5AMCyNhFkfB3Hb9Um18kxTlzh8zgHilznxTCY62/fgvcSGE2mPM\nPd5yHtXGWlmnbRKQrT1v0uTlTOSentJRedfa5qDbe4mOyWAVUlSnB39xG/3bxen5\nSWBj2x2ReeK2YnSL+xHkyYk9sDlzgw4ODcdPpM2gHprt9dqdkKxT+y0AiJJz/Hu/\nw53kKPBkp+Cf/4XJtPOafe4ncydD5Tj1XS9rKGvyOgOMV3UrDjh0To90FcGJNCL5\nxXyn94onAgMBAAECggEABlYbkhpz4sKHIcTWIAfPkHqNqqr90NCajInhMDPmeDP3\nNJI+MaVJzTLFGduBXfmd8tUto8ILE04MHyMyy9MluZ9zDTLfiUN/h2zXL+RlG/tt\nUW6QoIPFmVh7Z1PBS2c1fb4nQffVBEPxbh24cPBdp4LlaTnpxxWzUuCmI3rHqXHm\nVOoW66TTdn2fk8hhjJaYzCulL6/pOuRMMWCu3xvt+VeVHlpdq3J6CAxImAvHedMI\nxzfXd/Lcialv0geN1TI6EqUfDD7D1ZZqsrksNZM1inmUwK48LrSSYZjkm51voYzf\nFD7y5qKU8hq/FAV7flbh2wuAtSLubETGRKHLjpXIeQKBgQD7zEMNLDSZJymextbt\nUrk6Jh1v73kFFXDJv/CTEybO+3BTIBcJVjzXAG0mF7NERlUy6jiHee9aISXoTm8R\necNo+n1AngBz7bCTWRhT/eblSLVSMN2hwwgdQuqWpJZWFO7ZtR349K/VX0zBFPtF\n98Asgnmqg8X9X4s7JSzle1gWgwKBgQDvNF1Aft5AqP6CAF/oP7+g/eBvnxDtDg1R\nS6Pl24nxSMtFVa4wfq2gM10E98971Vq7VsxNWqo2W3CT85jKe0D3zRAGlZ0jjMl5\nIhUt8V2Vq6q6MvEIAVgesZtvOXb2K9f3h1BOdIP2WPRXGJDnuGY9j0u4UWW7SUAb\naBhYdfcMjQKBgC8lZNyfjU2r3ogjNPUEyzfPES33SdKg3Bh6fuIa8OZKgBKgbI/L\n/OJI6yb5wxAilytMXb9IHn/iuwVPQk6kXOlYFYG20+Dg/XHpebuoS8Zcoc685ZK3\nQNqxv9jrAlcl3j8XQYBu2El8aZOxiQblx67N01gRCk5RyHEPmeNx/+FfAoGARfYq\n0BJLLt4+kgdKBcOfaJbYbc04Rh02B/D3nuL3FXsU+NJ2f/iND632Jt3T8YQVZXWd\ni4JZBkz4QE2fApnKBrATX9mifCNRSfyN9UIC/SOYa506ofzCqTeJHp7QDHAGWn9Z\nHZk2f3bFADRPLXbhcF/Y5a/o8T4bYeiwNi9KcoECgYBGJ5NmQVy6ts19DpyWzK2+\nK8mG+vCx1rLfhwNW8ssrQsa+k9CE+krj/LflxfkHzQcOVoTgRxbHxT/TgBYCuoyE\nhnQb2L0bA/tayaMG2mz6rfBt6spliAaLl+4bvu6BWP4KY0jqg+mUsyrqumHNVgSp\nqqoHxy8uVFxNcMOw8AStmg==\n-----END PRIVATE KEY-----\n",
        "client_email": os.environ.get('CLIENT_EMAIL'),
        "client_id": os.environ.get('CLIENT_ID'),
        "auth_uri": os.environ.get('AUTH_URI'),
        "token_uri": os.environ.get('TOKEN_URI'),
        "auth_provider_x509_cert_url": os.environ.get('AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL')
    }

### Archives
# from PIL import Image
# from pyspark.sql import SparkSession
# from pyspark.sql import functions as F 

### Activate python environment
# source env/bin/activate

### Include Google Analytics tracking code (not working)
# with open("./templates/google_analytics.html", "r") as f:
#     html_code = f.read()
#     components.html(html_code, height=0)

### Set page config
st.set_page_config(page_title='Sotis Immobilier', 
                    page_icon = "https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_pure_darkbg_240px.ico",  
                    layout = 'wide',
                    initial_sidebar_state = 'expanded')

### Track the app with streamlit-analytics
### Analytics data will be stored in a Google Cloud Firestore database
if platform.node() != "MacBookPro-LudovicGardy.local":
    ### Secure way to store the firestore keys and provide them to start_tracking
    import json,tempfile
    tfile = tempfile.NamedTemporaryFile(mode="w+")
    json.dump(cred_dict, tfile)
    tfile.flush()
    streamlit_analytics.start_tracking(firestore_key_file=tfile.name, firestore_collection_name="sotisimmo_analytics")

    # streamlit_analytics.start_tracking()
    # streamlit_analytics.track(firestore_key_file="firestore-key.json", firestore_collection_name="sotisimmo_analytics")

### App
class PropertyApp:
    '''
    This class creates a Streamlit app that displays the average price of real estate properties in France, by department.
    The data is loaded from the French open data portal (https://www.data.gouv.fr/fr/), and the app is built with Streamlit.
    The app is not optimized for mobile devices, and the data is limited to the years 2018-2022. A new version will be released
    in the future, with more features and a better user experience. A streaming version of the app will come soon as well, with
    a Kafka cluster and a Spark Streaming job. Stay tuned! 

    Parameters
    ----------
    None

    Returns
    -------
    A Streamlit app
    '''
    
    def __init__(self):
        
        self.jitter_value = 0
        self.data_loaded = True  # Variable pour suivre si les données ont été chargées avec succès

        if 'selected_postcode_title' not in st.session_state:
            st.session_state.selected_postcode_title = None

        self.load_summarized_data()

        with st.sidebar:
            self.create_toolbar()
            self.load_data_and_initialize_params()

        self.create_plots()


    def create_toolbar(self):

        logo_path = "https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_pure_darkbg_240px.png"
        desired_width = 60

        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(logo_path, width=desired_width)
        with col2:
            st.write("# Sotis A.I.")

        st.caption("""Cette application a été pensée et créée par Ludovic Gardy, Sotis A.I.© 2023. 
                    Une prochaine version permettra d'afficher en direct les prix des biens pour l'année en cours. 
                    Pour en savoir plus ou pour me contacter, rendez-vous sur [sotisanalytics.com](https://www.sotisanalytics.com). Bonne visite !""")

        st.divider()


    def load_summarized_data(self):

        ### Download data summarized from AWS S3
        url = "https://sotisimmo.s3.eu-north-1.amazonaws.com/geo_dvf_summarized_summary.csv.gz"
        response = requests.get(url)

        ### Store data in a buffer
        buffer = BytesIO(response.content)

        ### Load data into a Pandas dataframe
        self.summarized_df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                dtype={"code_postal": str})

    def load_data_and_initialize_params(self):
        '''
        Load data from the French open data portal and initialize the parameters of the app.

        Parameters
        ----------
        None

        Returns
        -------
        self.df_pandas: Pandas dataframe
            The dataframe containing the data loaded from the French open data portal.
        self.selected_department: str
            The department selected by the user.
        self.selected_year: str
            The year selected by the user.
        self.selected_property_type: str
            The property type selected by the user.
        self.selected_mapbox_style: str
            The map style selected by the user.
        self.selected_colormap: str
            The colormap selected by the user.
        '''

        ### Load data 
        @st.cache_data
        def load_data(selected_dept, year):
            '''
            Load data from the French open data portal.
            @st.cache_data is used to cache the data, so that it is not reloaded every time the user changes a parameter.
            '''
            df_pandas = None  # Initialisez df_pandas à None ou pd.DataFrame()

            # Data from government are available only for the years 2018-2022
            try:
                if int(year) < 2023:
                    ### Download data from the French open data portal
                    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/{selected_dept}.csv.gz"
                    response = requests.get(url)

                    ### Store data in a buffer
                    buffer = BytesIO(response.content)

                    ### Load data into a Pandas dataframe
                    df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                            usecols=["type_local", "valeur_fonciere", "code_postal", "surface_reelle_bati", "longitude", "latitude"],
                                            dtype={"code_postal": str})
                else:
                    csv_path = f"https://sotisimmo.s3.eu-north-1.amazonaws.com/2023_merged/departements/{self.selected_department}.csv.gz"
                    df_pandas = pd.read_csv(csv_path, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                                usecols=["type_local", "valeur_fonciere", "code_postal", "surface_reelle_bati", "longitude", "latitude"],
                                                dtype={"code_postal": str})

                ### Remove rows with missing values
                df_pandas.dropna(inplace=True)

                ### Remove duplicates based on the columns "valeur_fonciere", "longitude", and "latitude"
                df_pandas.drop_duplicates(subset=["valeur_fonciere", "longitude", "latitude"], inplace=True, keep='last')

                ### Sort by postal code
                df_pandas = df_pandas.sort_values("code_postal")

                ### Add leading zeros to postal code
                df_pandas["code_postal"] = df_pandas["code_postal"].astype(float).astype(int).astype(str).str.zfill(5)

                print("")
                print(df_pandas["code_postal"])
                print("")
            except Exception as e:
                if df_pandas is None:
                    st.sidebar.error("Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(self.selected_department, self.selected_year))
                    st.session_state.data_load_error = True
                # st.warning(e)
                st.warning("Oups, un petit bug ici.")
                print(e)

            return df_pandas

        ### Set up the department selectbox
        departments = [str(i).zfill(2) for i in range(1, 96)]
        departments.append("971")
        departments.append("972")
        departments.append("973")
        departments.append("974")
        default_dept = departments.index("06")
        self.selected_department = st.selectbox("Département", departments, index=default_dept)

        # Check if the department has changed and reset the session state for the postcode if needed
        if 'previous_selected_department' in st.session_state and st.session_state.previous_selected_department != self.selected_department:
            if 'selected_postcode_title' in st.session_state:
                del st.session_state.selected_postcode_title
            if 'selected_postcode' in st.session_state:
                del st.session_state.selected_postcode

        # Update the previous selected department in the session state
        st.session_state.previous_selected_department = self.selected_department

        ### Set up the year selectbox
        years = ["Vendus en 2018", "Vendus en 2019", "Vendus en 2020", "Vendus en 2021", "Vendus en 2022", "En vente en 2023"]
        default_year = years.index("Vendus en 2022")
        self.selected_year = st.selectbox("Aannée", years, index=default_year).split(" ")[-1]

        ### Load data
        self.df_pandas = load_data(self.selected_department, self.selected_year)

        if not self.df_pandas is None:

            ### Set up a copy of the dataframe
            self.df_pandas = self.df_pandas.copy()

            ### Set up the property type selectbox
            property_types = sorted(self.df_pandas['type_local'].unique())
            selectbox_key = f"local_type_{self.selected_department}_{self.selected_year}"
            self.selected_property_type = st.selectbox("Type de bien", property_types, key=selectbox_key)

            ### Set up the normalization checkbox
            self.normalize_by_area = st.checkbox("Prix au m²", True)
            
            if self.normalize_by_area:
                self.df_pandas['valeur_fonciere'] = self.df_pandas['valeur_fonciere'] / self.df_pandas['surface_reelle_bati']

            # Ajoutez ceci après les autres éléments dans la barre latérale
            self.selected_plots = st.multiselect("Supprimer / ajouter des graphiques", 
                                                ["Carte", "Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4"],
                                                ["Carte", "Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4"])

    def calculate_median_difference(self, property_type):

        # Filter the summarized data for the given department
        dept_data = self.summarized_df_pandas[self.summarized_df_pandas['code_postal'] == self.selected_department]
        column_to_use = 'median_value_SQM' if self.normalize_by_area else 'median_value'


        
        type_data = dept_data[dept_data['type_local'] == property_type]
        type_data = type_data.sort_values(by="Year")

        # Calculate the annual differences
        type_data['annual_diff'] = type_data[column_to_use].diff()
        
        # Calculate the average annual difference (excluding NaN values)
        annual_average_diff = type_data['annual_diff'].dropna().mean()
        
        # Calculate percentage difference between 2018 and 2022
        try:
            value_2018 = type_data[type_data['Year'] == 2018][column_to_use].values[0]
            value_2022 = type_data[type_data['Year'] == 2022][column_to_use].values[0]
            percentage_diff = ((value_2022 - value_2018) / value_2018) * 100
        except IndexError:
            percentage_diff = "NA"
        

        return(annual_average_diff, percentage_diff)

    def create_plots(self):
        '''
        Create the plots.

        Parameters
        ----------
        None

        Returns
        -------
        Grphical representation
        '''

        if self.df_pandas is None:
            st.error("Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(self.selected_department, self.selected_year))
            return

        # Set the title of the section
        # st.markdown('# Sotis A.I. Immobilier')
        st.markdown('## Visualisez les prix de l\'immobilier en France')
        st.markdown("""
        🏠 Les graphiques interactifs ci-dessous représentent les valeurs immobilières des biens (maison, appartement, etc.) en France,
        en fonction de leur localisation géographique. La version pour **téléphone portable** 📳 de cette application fonctionne, mais doit encore être optimisée. 
        Si vous naviguez sur un téléphone, sachez que vous pouvez cliquer sur la **flèche en haut à gauche** ⬇️ de l'écran pour
        ouvrir le **menu latéral** ⚙️ qui vous permettra de choisir le département, l'année et le type de bien immobilier qui vous intéressent.
        """)

        ### Section 1
        if "Carte" in self.selected_plots:
            # Afficher l'alerte si l'année sélectionnée est 2023
            if "2023" in self.selected_year:
                st.warning("Attention : Les données tarifaires pour l'année 2023 proviennent directement d'agences immobilières et sont actualisées en continu. Il est important de noter que ces informations diffèrent des données gouvernementales disponibles pour les années antérieures (2018 à 2022). Par conséquent, nous vous recommandons d'exercer une vigilance accrue lors de leur interprétation. De plus, veuillez noter que la précision des localisations géographiques pour les biens immobiliers de 2023 est moins fiable que pour les années précédentes.")

            if 'selected_postcode_title' in st.session_state and st.session_state.selected_postcode_title:
                map_title = f"Distribution des prix médians pour les {self.selected_property_type.lower()}s dans le {st.session_state.selected_postcode_title} en {self.selected_year}"
            else:
                map_title = f"Distribution des prix médians pour les {self.selected_property_type.lower()}s dans le {self.selected_department} en {self.selected_year}"
            st.markdown(f"### {map_title}")
            self.plot_map()
            st.divider()

        ### Section 2
        if "Fig. 1" in self.selected_plots:
            # Afficher l'alerte si l'année sélectionnée est 2023
            if "2023" in self.selected_year:
                st.warning("Attention : Les données tarifaires pour l'année 2023 proviennent directement d'agences immobilières et sont actualisées en continu. Il est important de noter que ces informations diffèrent des données gouvernementales disponibles pour les années antérieures (2018 à 2022). Par conséquent, nous vous recommandons d'exercer une vigilance accrue lors de leur interprétation. De plus, veuillez noter que la précision des localisations géographiques pour les biens immobiliers de 2023 est moins fiable que pour les années précédentes.")

            st.markdown(f"### Fig 1. Distribution des prix médians dans le {self.selected_department} en {self.selected_year}")
            self.plot_1()
            st.divider()

        ### Section 3
        if "Fig. 2" in self.selected_plots:
            # Afficher l'alerte si l'année sélectionnée est 2023
            if "2023" in self.selected_year:
                st.warning("Attention : Les données tarifaires pour l'année 2023 proviennent directement d'agences immobilières et sont actualisées en continu. Il est important de noter que ces informations diffèrent des données gouvernementales disponibles pour les années antérieures (2018 à 2022). Par conséquent, nous vous recommandons d'exercer une vigilance accrue lors de leur interprétation. De plus, veuillez noter que la précision des localisations géographiques pour les biens immobiliers de 2023 est moins fiable que pour les années précédentes.")

            st.markdown(f"### Fig 2. Distribution des prix médians pour les {self.selected_property_type.lower()}s dans le {self.selected_department} en {self.selected_year}")
            st.markdown("""Les nombres au-dessus des barres représentent le nombre de biens par code postal. 
                        Ils fournissent un contexte sur le volume des ventes pour chaque zone.""")
            self.plot_2()
            st.divider()

        ### Section 4
        if "Fig. 3" in self.selected_plots:
            # Afficher l'alerte si l'année sélectionnée est 2023
            if "2023" in self.selected_year:
                st.warning("Attention : Les données tarifaires pour l'année 2023 proviennent directement d'agences immobilières et sont actualisées en continu. Il est important de noter que ces informations diffèrent des données gouvernementales disponibles pour les années antérieures (2018 à 2022). Par conséquent, nous vous recommandons d'exercer une vigilance accrue lors de leur interprétation. De plus, veuillez noter que la précision des localisations géographiques pour les biens immobiliers de 2023 est moins fiable que pour les années précédentes.")

            st.markdown(f"### Fig 3. Evolution des prix médians des {self.selected_property_type.lower()}s dans le {self.selected_department} entre 2018 et 2022")
            self.plot_3()
            st.divider()

        ### Section 5
        if "Fig. 4" in self.selected_plots:
            # Afficher l'alerte si l'année sélectionnée est 2023
            if "2023" in self.selected_year:
                st.warning("Attention : Les données tarifaires pour l'année 2023 proviennent directement d'agences immobilières et sont actualisées en continu. Il est important de noter que ces informations diffèrent des données gouvernementales disponibles pour les années antérieures (2018 à 2022). Par conséquent, nous vous recommandons d'exercer une vigilance accrue lors de leur interprétation. De plus, veuillez noter que la précision des localisations géographiques pour les biens immobiliers de 2023 est moins fiable que pour les années précédentes.")

            st.markdown(f"### Fig 4. Distribution des prix unitaires (par bien) dans votre quartier en {self.selected_year}")
            self.plot_4()

    def plot_map(self):

        col1, col2 = st.columns(2)  # Créer deux colonnes

        with col2:
            mapbox_styles = ["open-street-map", "carto-positron", "carto-darkmatter", "white-bg"]
            default_map = mapbox_styles.index("open-street-map")
            self.selected_mapbox_style = st.selectbox("🌏 Style de carte", mapbox_styles, index=default_map)

            colormaps = ["Rainbow", "Portland", "Jet", "Viridis", "Plasma", "Cividis", "Inferno", "Magma", "RdBu"]
            default_cmap = colormaps.index("Rainbow")
            self.selected_colormap = st.selectbox("🎨 Echelle de couleurs", colormaps, index=default_cmap)

        with col1:
            self.use_fixed_marker_size = st.checkbox("Fixer la taille des points", False)

            self.use_jitter = st.checkbox("Eviter la superposition des points", False)
            self.jitter_value = 0.001       

            self.remove_outliers = st.checkbox("Supprimer les valeurs extrêmes", True)
            st.caption("""Retirer les valeurs extrêmes (>1.5*IQR) permet d'améliorer la lisibilité de la carte.
                       Ces valeurs sont éliminées uniquement sur cette représentation, pas les prochaine.""")

        # Filtring the dataframe by property type
        filtered_df = self.df_pandas[self.df_pandas['type_local'] == self.selected_property_type]
        
        # Further filtering if a postcode is selected
        if hasattr(st.session_state, 'selected_postcode'):
            filtered_df = filtered_df[filtered_df['code_postal'] == st.session_state.selected_postcode]

        if self.remove_outliers:
            # Calculate Q1, Q3, and IQR
            Q1 = filtered_df['valeur_fonciere'].quantile(0.25)
            Q3 = filtered_df['valeur_fonciere'].quantile(0.75)
            IQR = Q3 - Q1
            # Calculate the upper fence (using 1.5xIQR)
            upper_fence = Q3 + 1.5 * IQR
            # Filter out outliers based on the upper fence
            filtered_df = filtered_df[filtered_df['valeur_fonciere'] <= upper_fence]

        # (Optional) Jittering : add a small random value to the coordinates to avoid overlapping markers
        self.jitter_value = 0.001 if self.use_jitter else 0
        filtered_df['longitude'] = filtered_df['longitude'].astype(float)
        filtered_df['latitude'] = filtered_df['latitude'].astype(float)
        filtered_df.loc[:, 'latitude'] = filtered_df['latitude'] + np.random.uniform(-self.jitter_value, self.jitter_value, size=len(filtered_df))
        filtered_df.loc[:, 'longitude'] = filtered_df['longitude'] + np.random.uniform(-self.jitter_value, self.jitter_value, size=len(filtered_df))

        
        # Add a column with a fixed size for all markers
        filtered_df = filtered_df.assign(marker_size=0.5)

        size_column = 'marker_size' if self.use_fixed_marker_size else 'valeur_fonciere'

        # Create the map
        fig = px.scatter_mapbox(filtered_df, 
                                lat='latitude', 
                                lon='longitude', 
                                color='valeur_fonciere', 
                                size=size_column, 
                                color_continuous_scale=self.selected_colormap, 
                                size_max=15, 
                                zoom=6, 
                                opacity=0.8, 
                                hover_data=['code_postal', 'valeur_fonciere', 'longitude', 'latitude'])
                        
        # Update the map style
        fig.update_layout(mapbox_style=self.selected_mapbox_style)
        fig.update_coloraxes(colorbar_thickness=10, colorbar_title_text="", colorbar_x=1, colorbar_xpad=0, colorbar_len=1.0, colorbar_y=0.5)
        fig.update_layout(height=800)

        st.plotly_chart(fig, use_container_width=True)

    def plot_1(self):
        grouped_data = self.df_pandas.groupby(["code_postal", "type_local"]).agg({
            "valeur_fonciere": "median"
        }).reset_index()

        # Triez grouped_data par code_postal
        grouped_data = grouped_data.sort_values("code_postal")

        # Réinitialisez l'index de grouped_data
        grouped_data = grouped_data.reset_index(drop=True)

        
        fig = px.line(grouped_data, x=grouped_data.index, y='valeur_fonciere', color='type_local', 
                    markers=True, labels={'valeur_fonciere': 'Average Price'})

        # Utilisez l'index pour tickvals et les codes postaux pour ticktext
        tickvals = grouped_data.index[::len(grouped_data['type_local'].unique())]
        ticktext = grouped_data['code_postal'].unique()
        
        # Utilisez tickvals et ticktext pour mettre à jour l'axe des x
        fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, range=[tickvals[0], tickvals[-1]], title_text = "Code postal")
        fig.update_yaxes(title_text='Prix médian en €')
        fig.update_layout(legend_orientation="h", 
                        legend=dict(y=1.1, x=0.5, xanchor='center', title_text=''),
                        height=600)
        st.plotly_chart(fig, use_container_width=True)

    def plot_2(self):

        # Check for orientation preference
        orientation = st.radio("Orientation", ["Barres horizontales (Grand écran)", "Barres verticales (Petit écran)"], label_visibility="hidden")

        # Filtring the dataframe by property type
        filtered_df = self.df_pandas[self.df_pandas['type_local'] == self.selected_property_type]

        # Grouping the dataframe by postal code and calculating the average property price
        grouped = filtered_df.groupby('code_postal').agg({
            'valeur_fonciere': 'median',
            'type_local': 'count'
        }).reset_index()

        # Renaming the columns
        grouped.columns = ['Postal Code', 'Property Value', 'Count']

        # Creation of the bar chart
        if orientation == "Barres horizontales (Grand écran)":
            fig = px.bar(grouped, x='Postal Code', y='Property Value')
            fig.update_layout(yaxis_title='Prix médian en €', xaxis_title='Code postal')
            fig.update_yaxes(type='linear')
            fig.update_xaxes(type='category')
            fig.update_layout(height=600)
        else:
            fig = px.bar(grouped, y='Postal Code', x='Property Value', orientation='h')
            fig.update_layout(xaxis_title='Prix médian en €', yaxis_title='Code postal')
            fig.update_yaxes(type='category')
            fig.update_xaxes(type='linear')
            fig.update_layout(height=1200)

        # Update the bar chart
        fig.update_traces(text=grouped['Count'], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)



    def plot_3(self):

        # Add a selectbox for choosing between bar and line plot
        #plot_types = ["Bar", "Line"]
        #selected_plot_type = st.selectbox("Selectionner une visualisation", plot_types, index=0)

        selected_plot_type = st.radio("Type", ["Graphique en barres", "Graphique en lignes"], label_visibility="hidden")

        # Determine the column to display
        value_column = 'median_value_SQM' if self.normalize_by_area else 'median_value'

        # Filter the dataframe by the provided department code
        dept_data = self.summarized_df_pandas[self.summarized_df_pandas['code_postal'] == self.selected_department]

        # Generate a brighter linear color palette
        years = sorted(dept_data['Year'].unique())
        property_types = dept_data['type_local'].unique()

        # Liste des couleurs bleues
        blue_palette = ['#08519c', '#3182bd', '#6baed6', '#bdd7e7', '#eff3ff']

        # Assurez-vous que le nombre de couleurs dans la palette correspond au nombre d'années
        if len(blue_palette) != len(years):
            st.error("Le nombre de couleurs dans la palette ne correspond pas au nombre d'années.")
            return

        if selected_plot_type == "Graphique en barres":
            cols = st.columns(len(property_types))

            # Associez chaque année à une couleur
            year_to_color = dict(zip(sorted(years), blue_palette))            

            for idx, prop_type in enumerate(property_types):
                annual_average_diff, percentage_diff = self.calculate_median_difference(prop_type)
                with cols[idx]:
                    if annual_average_diff > 0:
                        st.metric(label=prop_type, value=f"+{annual_average_diff:.2f} € / an", delta=f"{percentage_diff:.2f} % depuis 2018")
                    else:
                        st.metric(label=prop_type, value=f"{annual_average_diff:.2f} € / an", delta=f"{percentage_diff:.2f} % depuis 2018")

                    prop_data = dept_data[dept_data['type_local'] == prop_type]
                    
                    # Créez une liste pour stocker les tracés
                    traces = []
                    for year in prop_data['Year'].unique():
                        year_data = prop_data[prop_data['Year'] == year]
                        traces.append(go.Bar(x=year_data['Year'], y=year_data[value_column], name=str(year), marker_color=year_to_color[year]))
                    
                    layout = go.Layout(barmode='group', height=400, showlegend=False)

                    fig = go.Figure(data=traces, layout=layout)
                    st.plotly_chart(fig, use_container_width=True)

                    
        else:

            cols = st.columns(len(property_types))

            for idx, prop_type in enumerate(property_types):

                annual_average_diff, percentage_diff = self.calculate_median_difference(prop_type)

                with cols[idx]:
                    if annual_average_diff > 0:
                        st.metric(label=prop_type, value=f"+{annual_average_diff:.2f} € / an", delta=f"{percentage_diff:.2f} % depuis 2018")
                    else:
                        st.metric(label=prop_type, value=f"{annual_average_diff:.2f} € / an", delta=f"{percentage_diff:.2f} % depuis 2018")

            fig = px.line(dept_data, 
                          x='Year', 
                          y=value_column, 
                          color='type_local',
                          labels={"median_value": "Prix médian en €", "Year": "Année"},
                          markers=True,
                          height=600)

            fig.update_layout(xaxis_title="Type de bien",
                              yaxis_title="Prix médian en €",
                              legend_title="Type de bien",
                              height=600)
            fig.update_layout(legend_orientation="h", 
                            legend=dict(y=1.1, x=0.5, xanchor='center', title_text=''))
            
            st.plotly_chart(fig, use_container_width=True)


    def plot_4(self):

        unique_postcodes = self.df_pandas['code_postal'].unique()
                
        ### Set up the postal code selectbox and update button
        selected_postcode = st.selectbox("Code postal", sorted(unique_postcodes))

        col1, col2 = st.columns([1,3])
        with col1:
            if st.button(f"🌏 Actualiser la carte pour {selected_postcode}"):
                st.session_state.selected_postcode = selected_postcode
                st.session_state.selected_postcode_title = selected_postcode
                st.experimental_rerun()
        with col2:
            st.caption("""**'Actualiser la carte'** sert à rafraîchir la carte, tout en haut de la fenêtre, pour afficher les 
                       données de votre quartier spécifiquement au lieu d'afficher tout le département.""")
            

        # Si le bouton est cliqué, mettez à jour la carte avec les données du code postal sélectionné
        filtered_by_postcode = self.df_pandas[self.df_pandas['code_postal'] == selected_postcode]

        unique_property_types = filtered_by_postcode['type_local'].unique()

        # Créer le nombre approprié de colonnes
        cols = st.columns(len(unique_property_types))

        color_palette = sns.color_palette('tab10', len(unique_property_types)).as_hex()
        colors = dict(zip(unique_property_types, color_palette))

        for idx, property_type in enumerate(unique_property_types):

            subset = filtered_by_postcode[filtered_by_postcode['type_local'] == property_type]
            trace = go.Box(y=subset['valeur_fonciere'], 
                        name=property_type, 
                        marker_color=colors[property_type], 
                        boxpoints='all', 
                        jitter=0.3, 
                        pointpos=0, 
                        marker=dict(opacity=0.5))

            fig = go.Figure(data=[trace])
            fig.update_layout(yaxis_title='Prix médian en €')
            fig.update_layout(height=600)
            fig.update_layout(legend_orientation="h", legend=dict(y=1.1, x=0.5, xanchor='center'))
            fig.update_layout(margin=dict(t=20, b=80, l=50, r=50))
            
            # Retirer les labels des x
            fig.update_xaxes(showticklabels=False)

            # Ajoutez un titre en utilisant st.markdown() avant d'afficher le graphique
            with cols[idx]:
                st.markdown(f"<div style='text-align: center;'>{property_type}</div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)

                # # Ajouter un bouton pour afficher le DataFrame
                # if st.button(f"Afficher les données pour {property_type}"):
                    
                #     # Renommer les colonnes
                #     subset = subset.rename(columns={
                #         'code_postal': 'Code Postal',
                #         'type_local': 'Type',
                #         'valeur_fonciere': 'Valeur (€)',
                #         'surface_reelle_bati': 'Surface (m²)'
                #     })
                #     selected_columns = ['Code Postal', 'Type', 'Valeur (€)', 'Surface (m²)']
                #     subset = subset[selected_columns]

                #     # Afficher le DataFrame dans Streamlit
                #     st.dataframe(subset, hide_index=True)

if platform.node() != "MacBookPro-LudovicGardy.local":
    streamlit_analytics.stop_tracking(firestore_key_file=tfile.name, firestore_collection_name="sotisimmo_analytics")
    # streamlit_analytics.stop_tracking()

if __name__ == "__main__":
    PropertyApp()
