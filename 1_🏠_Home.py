"""
Home page for the Sotis Immobilier application.
This module handles the main page layout and user interactions.
"""

import streamlit as st

from src.components.charts.plotter import PropertyPlotter
from src.config.config import get_config
from src.config.departments import DEFAULT_DEPARTMENT, DEPARTMENTS
from src.config.property_types import DEFAULT_PROPERTY_TYPE, PROPERTY_TYPES
from src.config.years import AVAILABLE_YEARS, DEFAULT_YEAR
from src.core.data.loader import DataLoader


def initialize_session_state():
    """Initialize the session state variables with default values."""
    if "data_load_error" not in st.session_state:
        st.session_state.data_load_error = False
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = DEFAULT_YEAR
    if "selected_department" not in st.session_state:
        st.session_state.selected_department = DEFAULT_DEPARTMENT
    if "selected_local_type" not in st.session_state:
        st.session_state.selected_local_type = DEFAULT_PROPERTY_TYPE
    if "show_price_per_sqm" not in st.session_state:
        st.session_state.show_price_per_sqm = True
    if "remove_outliers" not in st.session_state:
        st.session_state.remove_outliers = True
    if "original_data" not in st.session_state:
        st.session_state.original_data = None


def create_sidebar():
    """Create the sidebar with user controls."""
    config = get_config()
    
    st.sidebar.image(
        config["page"].page_logo,
        width=100
    )
    
    st.sidebar.markdown(config["page"].sidebar_title)
    st.sidebar.caption(config["page"].page_description)
    st.sidebar.markdown("---")
    
    # Year selection
    st.sidebar.markdown("### 📅 Année")
    st.session_state.selected_year = st.sidebar.selectbox(
        "Sélectionnez l'année",
        options=AVAILABLE_YEARS,
        index=len(AVAILABLE_YEARS) - 1
    )
    
    # Department selection
    st.sidebar.markdown("### 📍 Département")
    department_options = list(DEPARTMENTS.keys())
    default_index = department_options.index(DEFAULT_DEPARTMENT)
    st.session_state.selected_department = st.sidebar.selectbox(
        "Sélectionnez le département",
        options=department_options,
        format_func=lambda x: f"{x} - {DEPARTMENTS[x]}",
        index=default_index
    )
    
    # Property type selection
    st.sidebar.markdown("### 🏠 Type de bien")
    property_type_options = list(PROPERTY_TYPES.keys())
    default_property_index = property_type_options.index(DEFAULT_PROPERTY_TYPE)
    st.session_state.selected_local_type = st.sidebar.selectbox(
        "Sélectionnez le type de bien",
        options=property_type_options,
        format_func=lambda x: PROPERTY_TYPES[x],
        index=default_property_index
    )

    # Price display option
    st.sidebar.markdown("### 💰 Affichage des prix")
    st.session_state.show_price_per_sqm = st.sidebar.checkbox(
        "Afficher les prix au m²",
        value=True,
        help="Affiche les prix au m² au lieu des prix totaux dans toutes les visualisations"
    )
    
    # Outliers option
    st.sidebar.markdown("### 📊 Filtrage des données")
    st.session_state.remove_outliers = st.sidebar.checkbox(
        "Supprimer les valeurs extrêmes",
        value=True,
        help="Supprime les valeurs extrêmes (>1.5*IQR) pour améliorer la lisibilité des visualisations"
    )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(config["page"].footer)


def main():
    """Main function to run the application."""
    # Initialize session state
    initialize_session_state()
    
    # Set page configuration
    config = get_config()
    st.set_page_config(
        page_title=config["page"].page_title,
        page_icon=config["page"].page_icon,
        layout=config["page"].layout,
        initial_sidebar_state=config["page"].initial_sidebar_state
    )
    
    # Create sidebar
    create_sidebar()
    
    # Load data
    properties_data = DataLoader.fetch_data_gouv(
        st.session_state.selected_department,
        st.session_state.selected_year
    )
    
    # Store original data and create filtered version if needed
    if properties_data is not None:
        st.session_state.original_data = properties_data.copy()
        
        # Create visualizations
        plotter = PropertyPlotter(
            properties_data=properties_data,
            selected_year=st.session_state.selected_year,
            selected_department=st.session_state.selected_department,
            show_price_per_sqm=st.session_state.show_price_per_sqm,
            selected_local_type=st.session_state.selected_local_type,
            remove_outliers=st.session_state.remove_outliers
        )
        plotter.create_visualization_tabs()


if __name__ == "__main__":
    main() 