"""
Visualization module for the Sotis Immobilier application.
This module handles all data visualization components using Plotly.
"""

from typing import List, Optional, Tuple

import folium
import hdbscan
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from branca.colormap import LinearColormap
from folium.plugins import MarkerCluster
from scipy import stats

from src.config.config import get_data_config


class PropertyPlotter:
    """Class responsible for creating property data visualizations."""

    def __init__(self, properties_data: pd.DataFrame, selected_year: int, selected_department: str, show_price_per_sqm: bool = False, selected_local_type: str = "Appartement", remove_outliers: bool = False):
        """
        Initialize the PropertyPlotter.
        
        Args:
            properties_data (pd.DataFrame): The property data to visualize.
            selected_year (int): The selected year for visualization.
            selected_department (str): The selected department for visualization.
            show_price_per_sqm (bool): Whether to show prices per square meter.
            selected_local_type (str): The selected property type.
            remove_outliers (bool): Whether to remove outliers from visualizations.
        """
        self.properties_data = properties_data.copy()
        self.selected_year = selected_year
        self.selected_department = selected_department
        self.config = get_data_config()
        self.show_price_per_sqm = show_price_per_sqm
        self.selected_local_type = selected_local_type
        self.remove_outliers = remove_outliers
        
        # Filter data by property type
        self.properties_data = self.properties_data[self.properties_data["type_local"] == self.selected_local_type]
        
        # Calculate price per square meter
        self.properties_data["prix_m2"] = self.properties_data["valeur_fonciere"] / self.properties_data["surface_reelle_bati"]
        
        # Remove outliers if needed
        if self.remove_outliers:
            self._remove_outliers()
        
        # Default visualization settings
        self.selected_mapbox_style = "open-street-map"
        self.selected_colormap = "Rainbow"
        self.marker_size = 10
        self.use_jitter = True
        self.use_clustering = False
        self.cluster_min_size = 5

    def _remove_outliers(self) -> None:
        """Remove outliers from the data using IQR method."""
        value_column = "prix_m2" if self.show_price_per_sqm else "valeur_fonciere"
        Q1 = self.properties_data[value_column].quantile(0.25)
        Q3 = self.properties_data[value_column].quantile(0.75)
        IQR = Q3 - Q1
        upper_fence = Q3 + 1.5 * IQR
        self.properties_data = self.properties_data[self.properties_data[value_column] <= upper_fence]

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
        price_type = "au m²" if self.show_price_per_sqm else "totaux"
        property_type = {
            "Appartement": "appartements",
            "Maison": "maisons",
            "Local industriel. commercial ou assimilé": "locaux commerciaux"
        }.get(self.selected_local_type, "biens")
        
        return f"""
        🏠 Les graphiques interactifs que vous découvrirez ci-dessous offrent une vue d'ensemble détaillée des valeurs immobilières 
        en France, spécifiquement pour les {property_type}. Grâce à la barre d'options 
        latérale, personnalisez votre expérience en sélectionnant le département, l'année et la catégorie de bien qui vous 
        intéressent. Vous aurez ainsi accès à un riche ensemble de données portant sur plusieurs millions de transactions 
        immobilières effectuées entre {years[0]} et {years[-1]}. Les prix sont affichés {price_type}.
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
        self.use_clustering = st.checkbox(
            "Utiliser le regroupement des points",
            value=True,
            help="Regroupe les points proches les uns des autres pour une meilleure lisibilité"
        )

        if not self.use_clustering:
            self.marker_size = st.slider(
                "🔘 Taille des points",
                min_value=1,
                max_value=20,
                value=10,
                step=1
            )
            self.use_jitter = st.checkbox("Eviter la superposition des points", False)
        else:
            self.cluster_min_size = st.slider(
                "👥 Taille minimale des groupes",
                min_value=2,
                max_value=20,
                value=5,
                step=1
            )

    def _create_clustered_map(self, filtered_df: pd.DataFrame) -> folium.Map:
        """
        Create a clustered map using Folium.
        
        Args:
            filtered_df (pd.DataFrame): The filtered data to display on the map.
            
        Returns:
            folium.Map: The created map with clustered markers.
        """
        # Create the base map
        center_lat = filtered_df['latitude'].mean()
        center_lon = filtered_df['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        # Create a color map
        value_column = "prix_m2" if self.show_price_per_sqm else "valeur_fonciere"
        min_price = filtered_df[value_column].min()
        max_price = filtered_df[value_column].max()
        colormap = LinearColormap(
            colors=['blue', 'green', 'yellow', 'orange', 'red'],
            vmin=min_price,
            vmax=max_price
        )
        colormap.add_to(m)

        # Create a marker cluster
        marker_cluster = MarkerCluster().add_to(m)

        # Add markers to the cluster
        for idx, row in filtered_df.iterrows():
            popup_text = f"""
                <b>Commune:</b> {row['nom_commune']}<br>
                <b>Code postal:</b> {row['code_postal']}<br>
                <b>Prix:</b> {row[value_column]:,.0f} €{('/m²' if self.show_price_per_sqm else '')}<br>
                <b>Surface:</b> {row['surface_reelle_bati']:,.0f} m²
            """
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=folium.Popup(popup_text, max_width=300),
                color=colormap(row[value_column]),
                fill=True,
                fill_color=colormap(row[value_column]),
                fill_opacity=0.7
            ).add_to(marker_cluster)

        return m

    def _plot_map(self) -> None:
        """Create and display the interactive map visualization."""
        filtered_df = self._prepare_map_data()
        
        if self.use_clustering:
            # Create and display the clustered map
            m = self._create_clustered_map(filtered_df)
            st.components.v1.html(m._repr_html_(), height=800)
        else:
            # Create and display the scatter map
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

        # Add additional columns
        filtered_df["marker_size"] = self.marker_size
        filtered_df["ville"] = filtered_df["code_postal"].astype(str) + " " + filtered_df["nom_commune"].astype(str)
        filtered_df["departement"] = filtered_df["code_postal"].astype(str).str[:2]
        filtered_df["valeur"] = filtered_df["prix_m2"] if self.show_price_per_sqm else filtered_df["valeur_fonciere"]

        return filtered_df

    def _update_map_layout(self, fig: go.Figure) -> None:
        """Update the map layout settings."""
        fig.update_layout(
            mapbox_style=self.selected_mapbox_style,
            height=800
        )
        fig.update_coloraxes(
            colorbar_thickness=10,
            colorbar_title_text="Prix au m²" if self.show_price_per_sqm else "Prix total",
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
        price_type = "au m²" if self.show_price_per_sqm else "totaux"
        property_type = {
            "Appartement": "appartements",
            "Maison": "maisons",
            "Local industriel. commercial ou assimilé": "locaux commerciaux"
        }.get(self.selected_local_type, "biens")
        
        st.markdown(
            f"### Distribution des prix médians {price_type} pour les {property_type} dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        value_column = "prix_m2" if self.show_price_per_sqm else "valeur_fonciere"
        grouped_data = (
            self.properties_data.groupby(["code_postal"])
            .agg({value_column: "median"})
            .reset_index()
            .sort_values("code_postal")
        )

        fig = px.line(
            grouped_data,
            x=grouped_data.index,
            y=value_column,
            markers=True,
            labels={value_column: "Prix médian en €" + ("/m²" if self.show_price_per_sqm else "")},
        )

        self._update_department_plot_layout(fig, grouped_data)
        st.plotly_chart(fig, use_container_width=True)

    def _update_department_plot_layout(self, fig: go.Figure, grouped_data: pd.DataFrame) -> None:
        """Update the department plot layout settings."""
        tickvals = grouped_data.index
        ticktext = grouped_data["code_postal"].unique()

        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            range=[tickvals[0], tickvals[-1]],
            title_text="Code postal",
        )
        fig.update_yaxes(title_text="Prix médian en €" + ("/m²" if self.show_price_per_sqm else ""))
        fig.update_layout(
            height=500,
        )

    def _plot_price_distribution(self) -> None:
        """Create and display price distribution plots."""
        price_type = "au m²" if self.show_price_per_sqm else "totaux"
        property_type = {
            "Appartement": "appartements",
            "Maison": "maisons",
            "Local industriel. commercial ou assimilé": "locaux commerciaux"
        }.get(self.selected_local_type, "biens")
        
        st.markdown(
            f"### Distribution des prix {price_type} pour les {property_type} dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        value_column = "prix_m2" if self.show_price_per_sqm else "valeur_fonciere"
        
        # Calculate statistics
        mean_value = self.properties_data[value_column].mean()
        median_value = self.properties_data[value_column].median()
        
        # Create histogram with KDE
        fig = go.Figure()
        
        # Add histogram
        fig.add_trace(go.Histogram(
            x=self.properties_data[value_column],
            nbinsx=50,
            name="Histogramme",
            opacity=0.7,
            marker_color='#1f77b4',
            showlegend=True
        ))
        
        # Add KDE
        kde = stats.gaussian_kde(self.properties_data[value_column])
        x_range = np.linspace(self.properties_data[value_column].min(), self.properties_data[value_column].max(), 100)
        y_range = kde(x_range)
        # Scale KDE to match histogram
        y_range = y_range * len(self.properties_data) * (x_range[1] - x_range[0])
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_range,
            name="Densité",
            line=dict(color='#ff7f0e', width=2),
            showlegend=True
        ))
        
        # Add mean line
        fig.add_vline(
            x=mean_value,
            line_dash="dash",
            line_color="red",
            annotation_text="Moyenne",
            annotation_position="top right",
            annotation=dict(
                font=dict(size=12, color="red"),
                bgcolor="white",
                bordercolor="red",
                borderwidth=1
            )
        )
        
        # Add median line
        fig.add_vline(
            x=median_value,
            line_dash="dash",
            line_color="green",
            annotation_text="Médiane",
            annotation_position="top right",
            annotation=dict(
                font=dict(size=12, color="green"),
                bgcolor="white",
                bordercolor="green",
                borderwidth=1
            )
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            title=dict(
                text=f"Distribution des prix {price_type}",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top'
            ),
            xaxis_title=f"Prix en €{('/m²' if self.show_price_per_sqm else '')}",
            yaxis_title="Nombre de transactions",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0.8)"
            ),
            hovermode="x unified",
            template="plotly_white"
        )
        
        # Add hover template
        fig.update_traces(
            hovertemplate="<b>Prix</b>: %{x:,.0f} €<br><b>Nombre</b>: %{y}<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _plot_commune_statistics(self) -> None:
        """Create and display commune-level statistics."""
        price_type = "au m²" if self.show_price_per_sqm else "totaux"
        property_type = {
            "Appartement": "appartements",
            "Maison": "maisons",
            "Local industriel. commercial ou assimilé": "locaux commerciaux"
        }.get(self.selected_local_type, "biens")
        
        st.markdown(
            f"### Statistiques par commune pour les {property_type} dans le :blue[{self.selected_department}] en :blue[{self.selected_year}] (prix {price_type})"
        )

        value_column = "prix_m2" if self.show_price_per_sqm else "valeur_fonciere"
        
        # Create a combined key for grouping
        self.properties_data["commune_key"] = self.properties_data["nom_commune"]
        
        commune_stats = (
            self.properties_data.groupby(["commune_key", "code_postal", "nom_commune"])
            .agg({
                value_column: ["count", "median", "mean", "std"],
                "surface_reelle_bati": ["median", "mean"]
            })
            .round(2)
        )

        # Flatten the multi-level columns
        commune_stats.columns = [
            "Nombre de transactions",
            "Prix médian",
            "Prix moyen",
            "Écart-type des prix",
            "Surface médiane",
            "Surface moyenne"
        ]
        
        # Reset index to make commune_key, code_postal and nom_commune regular columns
        commune_stats = commune_stats.reset_index()
        
        # Sort by code postal and then by commune name
        commune_stats = commune_stats.sort_values(["code_postal", "nom_commune"])
        
        # Format the display
        commune_stats["Prix médian"] = commune_stats["Prix médian"].map("{:,.0f} €".format)
        commune_stats["Prix moyen"] = commune_stats["Prix moyen"].map("{:,.0f} €".format)
        commune_stats["Écart-type des prix"] = commune_stats["Écart-type des prix"].map("{:,.0f} €".format)
        commune_stats["Surface médiane"] = commune_stats["Surface médiane"].map("{:,.0f} m²".format)
        commune_stats["Surface moyenne"] = commune_stats["Surface moyenne"].map("{:,.0f} m²".format)
        
        # Rename columns for display
        commune_stats = commune_stats.rename(columns={
            "commune_key": "Commune",
            "code_postal": "Code postal",
            "nom_commune": "Nom de la commune"
        })
        
        # Reorder columns
        commune_stats = commune_stats[[
            "Code postal",
            "Commune",
            "Nombre de transactions",
            "Prix médian",
            "Prix moyen",
            "Écart-type des prix",
            "Surface médiane",
            "Surface moyenne"
        ]]

        # Convert price columns back to numeric for styling
        commune_stats["Prix moyen"] = commune_stats["Prix moyen"].str.replace(" €", "").str.replace(",", "").astype(float)
        commune_stats["Prix médian"] = commune_stats["Prix médian"].str.replace(" €", "").str.replace(",", "").astype(float)
        commune_stats["Écart-type des prix"] = commune_stats["Écart-type des prix"].str.replace(" €", "").str.replace(",", "").astype(float)

        # Fill NaN values with 0 for styling purposes
        commune_stats = commune_stats.fillna(0)

        # Create a style function for the dataframe
        def style_price_cells(val):
            if pd.isna(val) or val == 0:
                return "background-color: #f0f0f0; color: #666666"  # Gris clair pour les valeurs manquantes
            try:
                # Normalize the value between 0 and 1
                min_price = commune_stats["Prix moyen"].min()
                max_price = commune_stats["Prix moyen"].max()
                if min_price == max_price:
                    return "background-color: #e6f3ff; color: black"  # Bleu très clair si toutes les valeurs sont identiques
                
                normalized = (val - min_price) / (max_price - min_price)
                
                # Create a color gradient from light blue to dark blue
                color = f"rgb({int(200 * (1 - normalized))}, {int(200 * (1 - normalized))}, {int(255 * (1 - normalized))})"
                return f"background-color: {color}; color: {'white' if normalized > 0.7 else 'black'}"
            except:
                return "background-color: #f0f0f0; color: #666666"  # Gris clair en cas d'erreur

        # Apply the style
        styled_df = commune_stats.style.applymap(
            style_price_cells,
            subset=["Prix moyen", "Prix médian", "Écart-type des prix"]
        ).format({
            "Prix moyen": "{:,.0f} €",
            "Prix médian": "{:,.0f} €",
            "Écart-type des prix": "{:,.0f} €"
        })

        # Display the styled table
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=500,
            hide_index=True
        ) 