"""
Home page for the Sotis Immobilier application.
This module handles the main page layout and user interactions.
"""

import streamlit as st

from src.components.charts.plotter import PropertyPlotter
from src.core.data.loader import DataLoader
from src.utils.config import get_config


def initialize_session_state():
    """Initialize the session state variables."""
    if "data_load_error" not in st.session_state:
        st.session_state.data_load_error = False
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = 2023
    if "selected_department" not in st.session_state:
        st.session_state.selected_department = "75"
    if "selected_local_type" not in st.session_state:
        st.session_state.selected_local_type = "Appartement"


def create_sidebar():
    """Create the sidebar with user controls."""
    config = get_config()
    
    st.sidebar.image(
        config["page"].page_logo,
        width=200
    )
    
    st.sidebar.markdown(config["page"].sidebar_title)
    st.sidebar.markdown("---")
    
    # Year selection
    st.sidebar.markdown("### 📅 Année")
    st.session_state.selected_year = st.sidebar.selectbox(
        "Sélectionnez l'année",
        options=config["data"].available_years_datagouv + [config["data"].available_years_datagouv[-1] + 1],
        index=len(config["data"].available_years_datagouv) - 1
    )
    
    # Department selection
    st.sidebar.markdown("### 📍 Département")
    departments = {
        "01": "Ain",
        "02": "Aisne",
        "03": "Allier",
        "04": "Alpes-de-Haute-Provence",
        "05": "Hautes-Alpes",
        "06": "Alpes-Maritimes",
        "07": "Ardèche",
        "08": "Ardennes",
        "09": "Ariège",
        "10": "Aube",
        "11": "Aude",
        "12": "Aveyron",
        "13": "Bouches-du-Rhône",
        "14": "Calvados",
        "15": "Cantal",
        "16": "Charente",
        "17": "Charente-Maritime",
        "18": "Cher",
        "19": "Chèvre",
        "21": "Corrèze",
        "22": "Côte-d'Or",
        "23": "Côtes-d'Armor",
        "24": "Creuse",
        "25": "Dordogne",
        "26": "Doubs",
        "27": "Drôme",
        "28": "Eure",
        "29": "Eure-et-Loir",
        "30": "Finistère",
        "31": "Gard",
        "32": "Gers",
        "33": "Gironde",
        "34": "Hérault",
        "35": "Ille-et-Vilaine",
        "36": "Indre",
        "37": "Indre-et-Loire",
        "38": "Isère",
        "39": "Jura",
        "40": "Landes",
        "41": "Loir-et-Cher",
        "42": "Loire",
        "43": "Haute-Loire",
        "44": "Loire-Atlantique",
        "45": "Loiret",
        "46": "Lot",
        "47": "Lot-et-Garonne",
        "48": "Lozère",
        "49": "Maine-et-Loire",
        "50": "Manche",
        "51": "Marne",
        "52": "Haute-Marne",
        "53": "Mayenne",
        "54": "Meurthe-et-Moselle",
        "55": "Meuse",
        "56": "Morbihan",
        "57": "Moselle",
        "58": "Nièvre",
        "59": "Nord",
        "60": "Oise",
        "61": "Orne",
        "62": "Pas-de-Calais",
        "63": "Puy-de-Dôme",
        "64": "Pyrénées-Atlantiques",
        "65": "Hautes-Pyrénées",
        "66": "Pyrénées-Orientales",
        "67": "Bas-Rhin",
        "68": "Haut-Rhin",
        "69": "Rhône",
        "70": "Haute-Saône",
        "71": "Saône-et-Loire",
        "72": "Sarthe",
        "73": "Savoie",
        "74": "Haute-Savoie",
        "75": "Paris",
        "76": "Seine-Maritime",
        "77": "Seine-et-Marne",
        "78": "Yvelines",
        "79": "Deux-Sèvres",
        "80": "Vosges",
        "81": "Yonne",
        "82": "Territoire de Belfort",
        "83": "Var",
        "84": "Vaucluse",
        "85": "Vendée",
        "86": "Vienne",
        "87": "Haute-Vienne",
        "88": "Vosges",
        "89": "Yonne",
        "90": "Territoire de Belfort",
        "91": "Essonne",
        "92": "Hauts-de-Seine",
        "93": "Seine-Saint-Denis",
        "94": "Val-de-Marne",
        "95": "Val-d'Oise",
    }
    
    st.session_state.selected_department = st.sidebar.selectbox(
        "Sélectionnez le département",
        options=list(departments.keys()),
        format_func=lambda x: f"{x} - {departments[x]}",
        index=0
    )
    
    # Property type selection
    st.sidebar.markdown("### 🏠 Type de bien")
    property_types = {
        "Appartement": "Appartement",
        "Maison": "Maison",
        "Local industriel. commercial ou assimilé": "Local commercial"
    }
    
    st.session_state.selected_local_type = st.sidebar.selectbox(
        "Sélectionnez le type de bien",
        options=list(property_types.keys()),
        format_func=lambda x: property_types[x],
        index=0
    )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(config["page"].page_description)


def main():
    """Main function to run the application."""
    # Initialize session state
    initialize_session_state()
    
    # Set page configuration
    # config = get_config()
    # st.set_page_config(
    #     page_title=config["page"].page_title,
    #     page_icon=config["page"].page_icon,
    #     layout=config["page"].layout,
    #     initial_sidebar_state=config["page"].initial_sidebar_state
    # )
    
    # Create sidebar
    create_sidebar()
    
    # Load data
    data_loader = DataLoader()
    properties_data = data_loader.fetch_data_gouv(
        st.session_state.selected_department,
        st.session_state.selected_year
    )
    
    # Create visualizations
    if properties_data is not None:
        plotter = PropertyPlotter(
            properties_data=properties_data,
            selected_year=st.session_state.selected_year,
            selected_department=st.session_state.selected_department
        )
        plotter.create_visualization_tabs()


if __name__ == "__main__":
    main() 