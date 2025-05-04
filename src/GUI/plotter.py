import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st


from ..config import get_data_URL

data_sources_origin = get_data_URL()


class Plotter:
    def __init__(self):
        print("Initializing Plotter...")

    def create_plots(self):
        """
        Create the plots.

        Parameters
        ----------
        None

        Returns
        -------
        Grphical representation
        """
        print("Creating plots...")

        # Set the title of the section
        # st.markdown('# Sotis A.I. Immobilier')
        st.markdown("## Visualisez les prix de l'immobilier en France")
        st.markdown(f"""
        🏠 Les graphiques interactifs que vous découvrirez ci-dessous offrent une vue d'ensemble détaillée des valeurs immobilières 
                    en France, réparties par type de bien : maisons, appartements et locaux commerciaux. Grâce à la barre d'options 
                    latérale, personnalisez votre expérience en sélectionnant le département, l'année et la catégorie de bien qui vous 
                    intéressent. Vous aurez ainsi accès à un riche ensemble de données portant sur plusieurs millions de transactions 
                    immobilières effectuées entre {data_sources_origin.get('available_years_datagouv')[0]} et {data_sources_origin.get('available_years_datagouv')[-1]}.
        """)

        self.tabs = st.tabs(["Carte", "Département", "Commune"])

        if self.properties_input is None:
            st.error(
                "Pas d'information disponible pour le département {} en {}. Sélectionnez une autre configuration.".format(
                    self.selected_department, self.selected_year
                )
            )
            return

        ### Section 1
        with self.tabs[0]:
            with st.container(border=True):
                self.plot_map_widgets()

        ### Section 2
        with self.tabs[1]:
            with st.container(border=True):
                self.plot_2()

            with st.container(border=True):
                self.plot_1()

        ### Section 4
        with self.tabs[2]:
            with st.container(border=True):
                self.plot_4()

    def plot_map_widgets(self):
        # Afficher l'alerte si l'année sélectionnée est 2024
        if (
            f"{data_sources_origin.get('available_years_datagouv')[-1]+1}"
            in self.selected_year
        ):
            st.warning(f"""⚠️ Les tarifs pour {data_sources_origin.get('available_years_datagouv')[-1]+1} sont mis à jour régulièrement par le robot Sotis-IMMO 🤖.
                        À la différence des données de {data_sources_origin.get('available_years_datagouv')[0]}-{data_sources_origin.get('available_years_datagouv')[-1]}, qui concernent des biens déjà vendus, celles de {data_sources_origin.get('available_years_datagouv')[-1]+1} présentent 
                        les offres en quasi temps-réel. Toutefois, elles sont moins précises sur le plan géographique, 
                        étant regroupées par zones approximatives, contrairement aux données des années précédentes, qui sont 
                        présentées par adresse.""")

        print("Creating map...")
        col1, col2 = st.columns(2)  # Créer deux colonnes

        with col2:
            mapbox_styles = [
                "open-street-map",
                "carto-positron",
                "carto-darkmatter",
                "white-bg",
            ]
            default_map = mapbox_styles.index("open-street-map")
            self.selected_mapbox_style = st.selectbox(
                "🌏 Style de carte", mapbox_styles, index=default_map
            )

            colormaps = [
                "Rainbow",
                "Portland",
                "Jet",
                "Viridis",
                "Plasma",
                "Cividis",
                "Inferno",
                "Magma",
                "RdBu",
            ]
            default_cmap = colormaps.index("Rainbow")
            self.selected_colormap = st.selectbox(
                "🎨 Echelle de couleurs", colormaps, index=default_cmap
            )

        with col1:
            self.marker_size_slider = st.slider("🔘 Taille des points", min_value=1, max_value=20, value=10, step=1)

            self.use_jitter = st.checkbox("Eviter la superposition des points", True)

            self.remove_outliers = st.checkbox("Supprimer les valeurs extrêmes", True)
            st.caption("""Retirer les valeurs extrêmes (>1.5*IQR) permet d'améliorer la lisibilité de la carte.
                    Ces valeurs sont éliminées uniquement sur cette représentation, pas les prochaine.""")

        if (
            self.selected_year
            == data_sources_origin.get("available_years_datagouv")[-1] + 1
            and not self.use_jitter
        ):
            st.success(f"""💡 Pour une meilleure visibilité des données géographiques de {data_sources_origin.get('available_years_datagouv')[-1]+1}, il est conseillé de cocher la case
                        'Eviter la superposition des points' ci-dessus.""")

        self.plot_map()


    # @st.cache_data
    def plot_map(self):
        if not self.use_jitter:
            self.jitter_value = 0
        else:
            self.jitter_value = 0.01

        # Filtring the dataframe by property type
        filtered_df = self.properties_input[
            self.properties_input["type_local"] == self.selected_local_type
        ]

        # Rename columns
        filtered_df = filtered_df.rename(columns={"longitude": "lon", "latitude": "lat", "valeur_fonciere": "valeur"})

        if self.remove_outliers:
            # Calculate Q1, Q3, and IQR
            Q1 = filtered_df["valeur"].quantile(0.25)
            Q3 = filtered_df["valeur"].quantile(0.75)
            IQR = Q3 - Q1
            # Calculate the upper fence (using 1.5xIQR)
            upper_fence = Q3 + 1.5 * IQR
            # Filter out outliers based on the upper fence
            filtered_df = filtered_df[filtered_df["valeur"] <= upper_fence]

        # Cast coordinates and apply jitter
        filtered_df["lon"] = filtered_df["lon"].astype(float)
        filtered_df["lat"] = filtered_df["lat"].astype(float)
        filtered_df.loc[:, "lat"] += np.random.uniform(
            -self.jitter_value, self.jitter_value, size=len(filtered_df)
        )
        filtered_df.loc[:, "lon"] += np.random.uniform(
            -self.jitter_value, self.jitter_value, size=len(filtered_df)
        )

        # Fix marker size according to slider
        size_column = "marker_size"
        filtered_df = filtered_df.assign(marker_size=self.marker_size_slider)

        print(filtered_df.head())

        # Combine code postal and commune name
        filtered_df["ville"] = filtered_df["code_postal"].astype(str) + " " + filtered_df["nom_commune"].astype(str)

        # Add department code
        filtered_df["departement"] = filtered_df["code_postal"].astype(str).str[:2]

        # Create the map
        fig = px.scatter_mapbox(
            filtered_df,
            lat="lat",
            lon="lon",
            color="valeur",
            size=size_column,
            color_continuous_scale=self.selected_colormap,
            size_max=self.marker_size_slider,  # Dynamically adapt size_max
            zoom=6,
            opacity=0.8,
            hover_data=["ville", "valeur", "lon", "lat"],
        )

        # Update the map style
        fig.update_layout(mapbox_style=self.selected_mapbox_style)
        fig.update_coloraxes(
            colorbar_thickness=10,
            colorbar_title_text="",
            colorbar_x=1,
            colorbar_xpad=0,
            colorbar_len=1.0,
            colorbar_y=0.5,
        )
        fig.update_layout(height=800)

        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})


    # @st.cache_data
    def plot_1(self):
        st.markdown(
            f"### Distribution des prix médians pour tous les types de biens dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )

        print("Creating plot 1...")
        grouped_data = (
            self.properties_input.groupby(["code_postal", "type_local"])
            .agg({"valeur_fonciere": "median"})
            .reset_index()
        )

        # Triez grouped_data par code_postal
        grouped_data = grouped_data.sort_values("code_postal")

        # Réinitialisez l'index de grouped_data
        grouped_data = grouped_data.reset_index(drop=True)

        fig = px.line(
            grouped_data,
            x=grouped_data.index,
            y="valeur_fonciere",
            color="type_local",
            markers=True,
            labels={"valeur_fonciere": "Average Price"},
        )

        # Utilisez l'index pour tickvals et les codes postaux pour ticktext
        tickvals = grouped_data.index[:: len(grouped_data["type_local"].unique())]
        ticktext = grouped_data["code_postal"].unique()

        # Utilisez tickvals et ticktext pour mettre à jour l'axe des x
        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            range=[tickvals[0], tickvals[-1]],
            title_text="Code postal",
        )
        fig.update_yaxes(title_text="Prix médian en €")
        fig.update_layout(
            legend_orientation="h",
            legend=dict(y=1.1, x=0.5, xanchor="center", title_text=""),
            height=600,
        )
        st.plotly_chart(fig, use_container_width=True)

    def plot_2(self):
        st.markdown(
            f"### Distribution des prix médians pour les :blue[{self.selected_local_type.lower()}s] dans le :blue[{self.selected_department}] en :blue[{self.selected_year}]"
        )
        st.markdown("""Les nombres au-dessus des barres représentent le nombre de biens par code postal. 
                    Ils fournissent un contexte sur le volume des ventes pour chaque zone.""")

        print("Creating plot 2 widgets...")

        # Check for orientation preference
        self.orientation = st.radio(
            "Orientation",
            ["Barres horizontales (Grand écran)", "Barres verticales (Petit écran)"],
            label_visibility="hidden",
        )

        print("Creating plot 2...")

        # Filtring the dataframe by property type
        filtered_df = self.properties_input[
            self.properties_input["type_local"] == self.selected_local_type
        ]

        # Grouping the dataframe by postal code and calculating the average property price
        grouped = (
            filtered_df.groupby("code_postal")
            .agg({"valeur_fonciere": "median", "type_local": "count"})
            .reset_index()
        )

        # Renaming the columns
        grouped.columns = ["Postal Code", "Property Value", "Count"]

        # Creation of the bar chart
        if self.orientation == "Barres horizontales (Grand écran)":
            fig = px.bar(grouped, x="Postal Code", y="Property Value")
            fig.update_layout(yaxis_title="Prix médian en €", xaxis_title="Code postal")
            fig.update_yaxes(type="linear")
            fig.update_xaxes(type="category")
            fig.update_layout(height=600)
        else:
            fig = px.bar(grouped, y="Postal Code", x="Property Value", orientation="h")
            fig.update_layout(xaxis_title="Prix médian en €", yaxis_title="Code postal")
            fig.update_yaxes(type="category")
            fig.update_xaxes(type="linear")
            fig.update_layout(height=1200)

        # Update the bar chart
        fig.update_traces(text=grouped["Count"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    def plot_3_condition(self):
        if (
            int(self.selected_year)
            != int(data_sources_origin.get("available_years_datagouv")[0])
            and int(self.selected_year)
            != int(data_sources_origin.get("available_years_datagouv")[-1]) + 1
        ):
            st.markdown(
                f"""### Evolution des prix médians des :blue[{self.selected_local_type.lower()}s] dans le :blue[{self.selected_department}] entre :blue[{int(self.selected_year)-1}] et :blue[{self.selected_year}]"""
            )
            self.plot_3()
        elif int(self.selected_year) == int(
            data_sources_origin.get("available_years_datagouv")[0]
        ):
            st.warning(
                "La figure ne peut pas être calculée car l'année sélectionnée est 2018. Or, les données de 2017 ne sont pas connues pas ce programme."
            )
            st.divider()
        elif int(self.selected_year) == int(
            data_sources_origin.get("available_years_datagouv")[-1] + 1
        ):
            st.warning("La figure ne peut pas être calculée pour l'année 2024.")
            st.divider()

    def plot_4(self):
        self.fig4_title = st.empty()
        self.fig4_title.markdown(
            f"###Distribution des prix unitaires pour tous les types de biens dans le :blue[votre quartier] en :blue[{self.selected_year}]"
        )

        print("Creating plot 4 widgets...")
        unique_postcodes = self.properties_input["code_postal"].unique()

        ### Set up the postal code selectbox and update button
        self.selected_postcode = st.selectbox("Code postal", sorted(unique_postcodes))

        print("Creating plot 4...")

        self.fig4_title.markdown(
            f"### Distribution des prix unitaires pour tous les types de biens dans le :blue[{self.selected_postcode}] en :blue[{self.selected_year}]"
        )

        # Si le bouton est cliqué, mettez à jour la carte avec les données du code postal sélectionné
        filtered_by_postcode = self.properties_input[
            self.properties_input["code_postal"] == self.selected_postcode
        ]

        unique_local_types = filtered_by_postcode["type_local"].unique()

        # Créer le nombre approprié de colonnes
        cols = st.columns(len(unique_local_types))

        color_palette = sns.color_palette("tab10", len(unique_local_types)).as_hex()
        colors = dict(zip(unique_local_types, color_palette))

        for idx, local_type in enumerate(unique_local_types):
            subset = filtered_by_postcode[
                filtered_by_postcode["type_local"] == local_type
            ]
            trace = go.Box(
                y=subset["valeur_fonciere"],
                name=local_type,
                marker_color=colors[local_type],
                boxpoints="all",
                jitter=0.3,
                pointpos=0,
                marker=dict(opacity=0.5),
            )

            fig = go.Figure(data=[trace])
            fig.update_layout(yaxis_title="Prix médian en €")
            fig.update_layout(height=600)
            fig.update_layout(
                legend_orientation="h", legend=dict(y=1.1, x=0.5, xanchor="center")
            )
            fig.update_layout(margin=dict(t=20, b=80, l=50, r=50))

            # Retirer les labels des x
            fig.update_xaxes(showticklabels=False)

            # Ajoutez un titre en utilisant st.markdown() avant d'afficher le graphique
            with cols[idx]:
                st.markdown(
                    f"<div style='text-align: center;'>{local_type}</div>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig, use_container_width=True)
