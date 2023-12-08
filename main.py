### Absolute imports
import streamlit as st
import streamlit_analytics
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
import pandas as pd
import platform
import tempfile
import json
import sys

### Relative imports
from modules.config import firebase_credentials, page_config, data_URL, azure_credentials, bigquery_credentials
from modules.data_loader import fetch_summarized_data, fetch_data_gouv, fetch_data_BigQuery
from modules.plots import Plotter
firebase_cred = firebase_credentials()
azure_cred = azure_credentials()
bigquery_cred = bigquery_credentials()
data_gouv_dict = data_URL()

if firebase_cred:
    ### Secure way to store the firestore keys and provide them to start_tracking
    tfile = tempfile.NamedTemporaryFile(mode='w+')
    json.dump(firebase_cred, tfile)
    tfile.flush()
    streamlit_analytics.start_tracking(firestore_key_file=tfile.name, firestore_collection_name='sotisimmo_analytics')
else:
    print("No credentials were found. Analytics will not be tracked.")

### Set page config
st.set_page_config(page_title=page_config().get('page_title'), 
                    page_icon = page_config().get('page_icon'),  
                    layout = page_config().get('layout'),
                    initial_sidebar_state = page_config().get('initial_sidebar_state'))

### App
class PropertyApp(Plotter):
    '''
    This class creates a Streamlit app that displays the average price of real estate properties in France, by department.

    Parameters
    ----------
    None

    Returns
    -------
    A Streamlit app
    '''
    
    def __init__(self):
        '''
        Initialize the app.
        '''
        
        print("Init the app...")


        st.markdown(page_config().get('markdown'), unsafe_allow_html=True)

        ### Init parameters
        self.data_loaded = True  # Variable to check if the data has been loaded

        if 'selected_postcode_title' not in st.session_state:
            st.session_state.selected_postcode_title = None

        self.summarized_df_pandas = fetch_summarized_data()

        with st.sidebar:
            self.steup_sidebar()
            self.initial_request()

        if isinstance(self.df_pandas, pd.DataFrame):
            if self.local_types:
                self.create_plots()
            else:
                st.sidebar.error("Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(self.selected_department, self.selected_year))

    def steup_sidebar(self):
        '''
        Set up the sidebar.
        '''

        logo_path = page_config().get('page_logo')
        desired_width = 60

        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(logo_path, width=desired_width)
        with col2:
            st.write('# Sotis A.I.')

        st.caption('''Ce prototype propose de répondre à un besoin de lecture plus claire du marché immobilier. 
                   \nRendez-vous sur https://www.sotisanalytics.com pour en savoir plus, signaler un problème, une idée ou pour me contacter. Bonne visite ! 
                   \nSotis A.I.© 2023''')

        st.divider()

    def initial_request(self):
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
        self.selected_local_type: str
            The property type selected by the user.
        self.selected_mapbox_style: str
            The map style selected by the user.
        self.selected_colormap: str
            The colormap selected by the user.
        '''

        ### Set up the department selectbox
        departments = [str(i).zfill(2) for i in range(1, 96)]
        departments.remove('20')
        departments.extend(['971', '972', '973', '974', '2A', '2B'])
        default_dept = departments.index('06')
        self.selected_department = st.selectbox('Département', departments, index=default_dept)

        # Check if the department has changed and reset the session state for the postcode if needed
        if 'previous_selected_department' in st.session_state and st.session_state.previous_selected_department != self.selected_department:
            if 'selected_postcode_title' in st.session_state:
                del st.session_state.selected_postcode_title
            if 'selected_postcode' in st.session_state:
                del st.session_state.selected_postcode

        # Update the previous selected department in the session state
        st.session_state.previous_selected_department = self.selected_department

        ### Set up the year selectbox
        years_range = data_gouv_dict.get('data_gouv_years')
        years = [f'Vendus en {year}' for year in years_range]
        default_year = years.index('Vendus en 2023')      

        # if True: # Tests
        #     years.extend(['En vente 2024'])
        #     default_year = years.index('En vente 2024')   
            
        self.selected_year = st.selectbox('Année', years, index=default_year).split(' ')[-1]

        ### Load data
        if '2024' not in self.selected_year:
            self.df_pandas = fetch_data_gouv(self.selected_department, self.selected_year)
        else:
            self.df_pandas = fetch_data_BigQuery(bigquery_cred, self.selected_department)

        if not self.df_pandas is None:

            ### Set up a copy of the dataframe
            self.df_pandas = self.df_pandas.copy()

            ### Set up the property type selectbox
            self.local_types = sorted(self.df_pandas['type_local'].unique())
            selectbox_key = f'local_type_{self.selected_department}_{self.selected_year}'
            self.selected_local_type = st.selectbox('Type de bien', self.local_types, key=selectbox_key)

            ### Set up the normalization checkbox
            self.normalize_by_area = st.checkbox('Prix au m²', True)
            
            if self.normalize_by_area:
                self.df_pandas['valeur_fonciere'] = (self.df_pandas['valeur_fonciere'] / self.df_pandas['surface_reelle_bati']).round().astype(int)

            # Ajoutez ceci après les autres éléments dans la barre latérale
            self.selected_plots = st.multiselect('Supprimer ou ajouter des graphiques', 
                                                ['Carte', 'Fig. 1', 'Fig. 2', 'Fig. 3', 'Fig. 4'],
                                                ['Carte', 'Fig. 1', 'Fig. 2', 'Fig. 3', 'Fig. 4'])
            
            ### Set up the chatbot
            st.divider()
            with st.expander("Chatbot (Optionnel)"):

                self.chatbot_checkbox = st.checkbox('Activer le chat bot', False)
                self.selected_model = st.selectbox('Modèle', ["GPT 3.5", "GPT 4", "Llama2-7B", "Llama2-13B", "Mistral"], index=1)
                self.model_api_key = st.text_input("Entrez une clé API 🔑", type="password", help="Trouvez votre clé [OpenAI](https://platform.openai.com/account/api-keys) ou [Replicate](https://replicate.com/account/api-tokens).")
                st.info("ℹ️ Votre clé API n'est pas conservée. Elle sera automatiquement supprimée lorsque vous fermerez ou rechargerez cette page.")

                if self.chatbot_checkbox:
                    if "GPT" in self.selected_model:
                        if not self.model_api_key:
                            st.warning('⚠️ Entrez une clé API **Open AI**.')
                    else:
                        # st.warning('⚠️ Entrez une clé API **Repliacte**.')
                        st.error('⚠️ Ce modèle n\'est pas encore disponible. Veuillez utiliser GPT.')
                    # st.stop()

                # st.markdown('Pour obtenir une clé API, rendez-vous sur le site de [openAI](https://platform.openai.com/api-keys).')

if firebase_cred:
    streamlit_analytics.stop_tracking(firestore_key_file=tfile.name, firestore_collection_name='sotisimmo_analytics')

if __name__ == '__main__':
    PropertyApp()
