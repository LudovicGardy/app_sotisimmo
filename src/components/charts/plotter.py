"""
Visualization module for the Sotis Immobilier application.
This module handles all data visualization components using Plotly.
"""

from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils.config import get_data_config


class PropertyPlotter:
    """Class responsible for creating property data visualizations."""

    def __init__(self, properties_data: pd.DataFrame, selected_year: int, selected_department: str):
        """
        Initialize the PropertyPlotter.
        
        Args:
            properties_data (pd.DataFrame): The property data to visualize.
            selected_year (int): The selected year for visualization.
            selected_department (str): The selected department for visualization.
        """
        self.properties_data = properties_data
        self.selected_year = selected_year
        self.selected_department = selected_department
        self.config = get_data_config()
        
        # Default visualization settings
        self.selected_mapbox_style = "open-street-map"
        self.selected_colormap = "Rainbow"
        self.marker_size = 10
        self.use_jitter = True
        self.remove_outliers = True

    def create_visualization_tabs(self) -> None:
        """Create the main visualization tabs with their respective plots."""
        st.markdown("## Visualisez les prix de l'immobilier en France")
        st.markdown(self._get_introduction_text())

        tabs = st.tabs(["Carte", "Département", "Commune"])

        if self.properties_data is None:
            st.error(
                f"Pas d'information disponible pour le département {self.selected_department} "
                f"en {self.selected_year}. Sélectionnez une autre configuration."
            )
            return

        with tabs[0]:
            with st.container(border=True):
                self._create_map_controls()
                self._plot_map()

        with tabs[1]:
            with st.container(border=True):
                self._plot_department_statistics()
            with st.container(border=True):
                self._plot_price_distribution()

        with tabs[2]:
            with st.container(border=True):
                self._plot_commune_statistics()

    def _get_introduction_text(self) -> str:
        """Get the introduction text for the visualization section."""
        years = self.config.available_years_datagouv
        return f"""
        🏠 Les graphiques interactifs que vous découvrirez ci-dessous offrent une vue d'ensemble détaillée des valeurs immobilières 
        en France, réparties par type de bien : maisons, appartements et locaux commerciaux. Grâce à la barre d'options 
        latérale, personnalisez votre expérience en sélectionnant le département, l'année et la catégorie de bien qui vous 
        intéressent. Vous aurez ainsi accès à un riche ensemble de données portant sur plusieurs millions de transactions 
        immobilières effectuées entre {years[0]} et {years[-1]}.
        """

    def _create_map_controls(self) -> None:
        """Create the map control widgets."""
        if self.selected_year == self.config.available_years_datagouv[-1] + 1:
            st.warning(self._get_current_year_warning())

        col1, col2 = st.columns(2)

        with col2:
            self._create_map_style_controls()
        with col1:
            self._create_map_data_controls()

    def _create_map_style_controls(self) -> None:
        """Create the map style control widgets."""
        mapbox_styles = [
            "open-street-map",
            "carto-positron",
            "carto-darkmatter",
            "white-bg",
        ]
        self.selected_mapbox_style = st.selectbox(
            "🌏 Style de carte",
            mapbox_styles,
            index=mapbox_styles.index("open-street-map")
        )

        colormaps = [
            "Rainbow", "Portland", "Jet", "Viridis",
            "Plasma", "Cividis", "Inferno", "Magma", "RdBu"
        ]
        self.selected_colormap = st.selectbox(
            "🎨 Echelle de couleurs",
            colormaps,
            index=colormaps.index("Rainbow")
        )

    def _create_map_data_controls(self) -> None:
        """Create the map data control widgets."""
        self.marker_size = st.slider(
            "🔘 Taille des points",
            min_value=1,
            max_value=20,
            value=10,
            step=1
        )

        self.use_jitter = st.checkbox("Eviter la superposition des points", True)
        self.remove_outliers = st.checkbox("Supprimer les valeurs extrêmes", True)
        
        st.caption("""
            Retirer les valeurs extrêmes (>1.5*IQR) permet d'améliorer la lisibilité de la carte.
            Ces valeurs sont éliminées uniquement sur cette représentation, pas les prochaine.
        """)

    def _plot_map(self) -> None:
        """Create and display the interactive map visualization."""
        filtered_df = self._prepare_map_data()
        
        fig = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lon",
            color="valeur",
            size="marker_size",
            color_continuous_scale=self.selected_colormap,
            size_max=self.marker_size,
            zoom=6,
            opacity=0.8,
            hover_data=["ville", "valeur", "lon", "lat"],
        )

        self._update_map_layout(fig)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    def _prepare_map_data(self) -> pd.DataFrame:
        """Prepare the data for map visualization."""
        filtered_df = self.properties_data.copy()
        
        # Apply jitter if needed
        jitter_value = 0.01 if self.use_jitter else 0
        filtered_df["lat"] = filtered_df["latitude"].astype(float) + np.random.uniform(
            -jitter_value, jitter_value, size=len(filtered_df)
        )
        filtered_df["lon"] = filtered_df["longitude"].astype(float) + np.random.uniform(
            -jitter_value, jitter_value, size=len(filtered_df)
        )

        # Remove outliers if needed
        if self.remove_outliers:
            Q1 = filtered_df["valeur_fonciere"].quantile(0.25)
            Q3 = filtered_df["valeur_fonciere"].quantile(0.75)
            IQR = Q3 - Q1
            upper_fence = Q3 + 1.5 * IQR
            filtered_df = filtered_df[filtered_df["valeur_fonciere"] <= upper_fence]

        # Add additional columns
        filtered_df["marker_size"] = self.marker_size
        filtered_df["ville"] = filtered_df["code_postal"].astype(str) + " " + filtered_df["nom_commune"].astype(str)
        filtered_df["departement"] = filtered_df["code_postal"].astype(str).str[:2]
        filtered_df["valeur"] = filtered_df["valeur_fonciere"]

        return filtered_df

    def _update_map_layout(self, fig: go.Figure) -> None:
        """Update the map layout settings."""
        fig.update_layout(
            mapbox_style=self.selected_mapbox_style,
            height=800
        )
        fig.update_coloraxes(
            colorbar_thickness=10,
            colorbar_title_text="",
            colorbar_x=1,
            colorbar_xpad=0,
            colorbar_len=1.0,
            colorbar_y=0.5,
        )

    def _get_current_year_warning(self) -> str:
        """Get the warning text for current year data."""
        return f"""⚠️ Les tarifs pour {self.config.available_years_datagouv[-1]+1} sont mis à jour régulièrement par le robot Sotis-IMMO 🤖.
                À la différence des données de {self.config.available_years_datagouv[0]}-{self.config.available_years_datagouv[-1]}, qui concernent des biens déjà vendus, celles de {self.config.available_years_datagouv[-1]+1} présentent 
                les offres en quasi temps-réel. Toutefois, elles sont moins précises sur le plan géographique, 
                étant regroupées par zones approximatives, contrairement aux données des années précédentes, qui sont 
                présentées par adresse."""

    def _plot_department_statistics(self) -> None:
        """Create and display department-level statistics."""
        st.markdown(
            f"### Distribution des prix médians pour tous les types de biens dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        grouped_data = (
            self.properties_data.groupby(["code_postal", "type_local"])
            .agg({"valeur_fonciere": "median"})
            .reset_index()
            .sort_values("code_postal")
        )

        fig = px.line(
            grouped_data,
            x=grouped_data.index,
            y="valeur_fonciere",
            color="type_local",
            markers=True,
            labels={"valeur_fonciere": "Prix médian en €"},
        )

        self._update_department_plot_layout(fig, grouped_data)
        st.plotly_chart(fig, use_container_width=True)

    def _update_department_plot_layout(self, fig: go.Figure, grouped_data: pd.DataFrame) -> None:
        """Update the department plot layout settings."""
        tickvals = grouped_data.index[:: len(grouped_data["type_local"].unique())]
        ticktext = grouped_data["code_postal"].unique()

        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            range=[tickvals[0], tickvals[-1]],
            title_text="Code postal",
        )
        fig.update_yaxes(title_text="Prix médian en €")
        fig.update_layout(
            legend_orientation="h",
            legend_title_text="Type de bien",
            height=500,
        )

    def _plot_price_distribution(self) -> None:
        """Create and display price distribution plots."""
        st.markdown(
            f"### Distribution des prix pour tous les types de biens dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        fig = px.box(
            self.properties_data,
            x="type_local",
            y="valeur_fonciere",
            color="type_local",
            labels={
                "type_local": "Type de bien",
                "valeur_fonciere": "Prix en €"
            }
        )

        fig.update_layout(
            showlegend=False,
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    def _plot_commune_statistics(self) -> None:
        """Create and display commune-level statistics."""
        st.markdown(
            f"### Statistiques par commune dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        commune_stats = (
            self.properties_data.groupby(["nom_commune", "type_local"])
            .agg({
                "valeur_fonciere": ["count", "median", "mean", "std"],
                "surface_reelle_bati": ["median", "mean"]
            })
            .round(2)
        )

        commune_stats.columns = [
            "Nombre de transactions",
            "Prix médian",
            "Prix moyen",
            "Écart-type des prix",
            "Surface médiane",
            "Surface moyenne"
        ]

        st.dataframe(
            commune_stats,
            use_container_width=True,
            height=500
        ) 