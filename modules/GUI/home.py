### Absolute imports
import json
import tempfile

import pandas as pd
import streamlit as st

from modules.data_loader import (
    fetch_data_gouv,
    fetch_summarized_data,
)
from modules.GUI.plotter import Plotter

### Relative imports
from ..config import (
    get_data_URL,
    get_page_config,
)
from .ui_components import display_sidebar

data_sources_origin = get_data_URL()


class Home(Plotter):
    """
    This class creates a Streamlit app that displays the average price of real estate properties in France, by department.
    """

    def __init__(self):
        print("Init the app...")

        st.markdown(get_page_config().get("markdown"), unsafe_allow_html=True)

        self.data_loaded = True  # Variable to check if the data has been loaded
        self.properties_summarized = fetch_summarized_data()

        with st.sidebar:
            display_sidebar()
            self.initial_request()

        if isinstance(self.properties_input, pd.DataFrame):
            if self.local_types:
                self.create_plots()
            else:
                st.sidebar.error(
                    "Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(
                        self.selected_department, self.selected_year
                    )
                )

    def initial_request(self):
        """
        Load data from the French open data portal and initialize the parameters of the app.

        Parameters
        ----------
        None

        Returns
        -------
        self.properties_input: Pandas dataframe
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
        """

        ### Set up the department selectbox
        departments = [str(i).zfill(2) for i in range(1, 96)]
        departments.remove("20")
        departments.extend(["971", "972", "973", "974", "2A", "2B"])
        default_dept = departments.index("06")
        self.selected_department = st.selectbox(
            "Département", departments, index=default_dept
        )

        # Check if the department has changed and reset the session state for the postcode if needed
        if (
            "previous_selected_department" in st.session_state
            and st.session_state.previous_selected_department
            != self.selected_department
        ):
            if "selected_postcode_title" in st.session_state:
                del st.session_state.selected_postcode_title
            if "selected_postcode" in st.session_state:
                del st.session_state.selected_postcode

        # Update the previous selected department in the session state
        st.session_state.previous_selected_department = self.selected_department

        ### Set up the year selectbox
        years_range = data_sources_origin.get("available_years_datagouv")
        if years_range:
            years = [f"Vendus en {year}" for year in years_range]
            default_year = years.index(f"Vendus en {years_range[-1]}")
        else:
            st.error("No available years found in data sources.")
            return

        # if True: # Tests
        #     years.extend(['En vente 2024'])
        #     default_year = years.index('En vente 2024')

        self.selected_year = st.selectbox("Année", years, index=default_year).split(
            " "
        )[-1]

        ### Load data
        self.properties_input = fetch_data_gouv(
            self.selected_department, self.selected_year
        )

        if self.properties_input is not None:
            ### Set up a copy of the dataframe
            self.properties_input = self.properties_input.copy()

            ### Set up the property type selectbox
            self.local_types = sorted(self.properties_input["type_local"].unique())
            selectbox_key = (
                f"local_type_{self.selected_department}_{self.selected_year}"
            )
            self.selected_local_type = st.selectbox(
                "Type de bien", self.local_types, key=selectbox_key
            )

            ### Set up the normalization checkbox
            self.normalize_by_area = st.checkbox("Prix au m²", True)

            if self.normalize_by_area:
                self.properties_input["valeur_fonciere"] = (
                    (
                        self.properties_input["valeur_fonciere"]
                        / self.properties_input["surface_reelle_bati"]
                    )
                    .round()
                    .astype(int)
                )

            ### Set up the chatbot
            st.divider()
            with st.expander("Chatbot (Optionnel)"):
                self.chatbot_checkbox = st.checkbox("Activer le chat bot", False)
                self.selected_model = st.selectbox(
                    "Modèle",
                    ["GPT 3.5", "GPT 4", "Llama2-7B", "Llama2-13B", "Mistral"],
                    index=1,
                )
                self.model_api_key = st.text_input(
                    "Entrez une clé API 🔑",
                    type="password",
                    help="Trouvez votre clé [OpenAI](https://platform.openai.com/account/api-keys) ou [Replicate](https://replicate.com/account/api-tokens).",
                )
                st.info(
                    "ℹ️ Votre clé API n'est pas conservée. Elle sera automatiquement supprimée lorsque vous fermerez ou rechargerez cette page."
                )

                if self.chatbot_checkbox:
                    if "GPT" in self.selected_model:
                        if not self.model_api_key:
                            st.warning("⚠️ Entrez une clé API **Open AI**.")
                    else:
                        # st.warning('⚠️ Entrez une clé API **Repliacte**.')
                        st.error(
                            "⚠️ Ce modèle n'est pas encore disponible. Veuillez utiliser GPT."
                        )
                    # st.stop()

                # st.markdown('Pour obtenir une clé API, rendez-vous sur le site de [openAI](https://platform.openai.com/api-keys).')

if __name__ == "__main__":
    Home()
