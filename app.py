import streamlit as st
import requests
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from PIL import Image
import seaborn as sns
import numpy as np
import matplotlib.cm as cm

# from pyspark.sql import SparkSession
# from pyspark.sql import functions as F
# import os

# source env/bin/activate
##

def shorten_titles(title):
    mapping = {
        "Local industriel. commercial ou assimilé": "local commercial",
        # Ajoutez d'autres mappages au besoin
    }
    return mapping.get(title, title) 

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
        st.set_page_config(layout="wide")
        self.jitter_value = 0

        if 'selected_postcode_title' not in st.session_state:
            st.session_state.selected_postcode_title = None

        self.load_summarized_data()

        with st.sidebar:
            self.create_toolbar()
            self.load_data_and_initialize_params()

        self.create_plots()

    def create_toolbar(self):

        logo_path = "https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_light_70px.png"
        desired_width = 60

        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(logo_path, width=desired_width)
        with col2:
            st.write("# Sotis A.I.")

        st.caption("""Cette application a été imaginée et développée par Ludovic Gardy, Sotis A.I.© 2023. 
                    Une prochaine version permettra d'afficher en direct les prix des biens pour l'année en cours. 
                    Rendez-vous sur [sotisanalytics.com](https://sotisanalytics.com) pour en savoir plus ou pour me contacter. Bonne visite !""")

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

            ### Download data from the French open data portal
            url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/{selected_dept}.csv.gz"
            response = requests.get(url)

            ### Store data in a buffer
            buffer = BytesIO(response.content)

            ### Load data into a Pandas dataframe
            df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                    usecols=["type_local", "valeur_fonciere", "code_postal", "surface_reelle_bati", "longitude", "latitude"],
                                    dtype={"code_postal": str})
            
            ### Remove rows with missing values
            df_pandas.dropna(inplace=True)

            ### Remove duplicates based on the columns "valeur_fonciere", "longitude", and "latitude"
            df_pandas.drop_duplicates(subset=["valeur_fonciere", "longitude", "latitude"], inplace=True, keep='last')

            ### Sort by postal code
            df_pandas = df_pandas.sort_values("code_postal")

            ### Add leading zeros to postal code
            df_pandas["code_postal"] = df_pandas["code_postal"].astype(str).str.zfill(5)

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
        years = [str(y) for y in range(2018, 2023)]
        default_year = years.index("2022")
        self.selected_year = st.selectbox("Aannée", years, index=default_year)

        ### Load data
        self.df_pandas = load_data(self.selected_department, self.selected_year).copy()

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



    def calculate_median_difference(self):

        # Filter the summarized data for the given department
        dept_data = self.summarized_df_pandas[self.summarized_df_pandas['code_postal'] == self.selected_department]
        column_to_use = 'median_value_SQM' if self.normalize_by_area else 'median_value'

        property_types = dept_data['type_local'].unique()
        annual_diffs = {}
        percentage_diffs = {}  # Store the percentage difference for each property type
        
        for property_type in property_types:
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
            
            annual_diffs[property_type] = annual_average_diff
            percentage_diffs[property_type] = percentage_diff

        col1, col2, col3 = st.columns(3)

        with col1:
            appartement_diff = annual_diffs.get(property_types[0], 0)
            appartement_percentage_diff = percentage_diffs.get(property_types[0], "NA")
            if appartement_diff > 0:
                st.metric(label="Appartements", value=f"+{appartement_diff:.2f} € / an", delta=f"{appartement_percentage_diff:.2f} %")
            else:
                st.metric(label="Appartements", value=f"{appartement_diff:.2f} € / an", delta=f"{appartement_percentage_diff:.2f} %")

        with col2:
            locaux_diff = annual_diffs.get(property_types[1], 0)
            locaux_percentage_diff = percentage_diffs.get(property_types[1], "NA")
            if locaux_diff > 0:
                st.metric(label="Locaux industriels", value=f"+{locaux_diff:.2f} € / an", delta=f"{locaux_percentage_diff:.2f} %")
            else:
                st.metric(label="Locaux industriels", value=f"{locaux_diff:.2f} € / an", delta=f"{locaux_percentage_diff:.2f} %")

        with col3:
            maison_diff = annual_diffs.get(property_types[2], 0)
            maison_percentage_diff = percentage_diffs.get(property_types[2], "NA")
            if maison_diff > 0:
                st.metric(label="Maisons", value=f"+{maison_diff:.2f} € / an", delta=f"{maison_percentage_diff:.2f} %")
            else:
                st.metric(label="Maisons", value=f"{maison_diff:.2f} € / an", delta=f"{maison_percentage_diff:.2f} %")

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
            if 'selected_postcode_title' in st.session_state and st.session_state.selected_postcode_title:
                map_title = f"Distribution des prix pour les {self.selected_property_type.lower()}s dans le {st.session_state.selected_postcode_title} en {self.selected_year}"
            else:
                map_title = f"Distribution des prix pour les {self.selected_property_type.lower()}s dans le {self.selected_department} en {self.selected_year}"
            st.markdown(f"### {map_title}")
            self.plot_1()
            st.divider()

        ### Section 2
        if "Fig. 1" in self.selected_plots:
            st.markdown(f"### Fig 1. Distribution des prix dans le {self.selected_department} en {self.selected_year}")
            self.plot_2()
            st.divider()

        ### Section 3
        if "Fig. 2" in self.selected_plots:
            st.markdown(f"### Fig 2. Distribution des prix pour les {self.selected_property_type.lower()}s dans le {self.selected_department} en {self.selected_year}")
            st.markdown("""Les nombres au-dessus des barres représentent le nombre de biens par code postal. 
                        Ils fournissent un contexte sur le volume des ventes pour chaque zone.""")
            self.plot_3()
            st.divider()

        ### Section 4
        if "Fig. 3" in self.selected_plots:
            st.markdown(f"### Fig 3. Evolution des prix des {self.selected_property_type.lower()}s dans le {self.selected_department} entre 2018 et 2022")
            self.calculate_median_difference()
            self.plot_4()
            st.divider()

        ### Section 5
        if "Fig. 4" in self.selected_plots:
            st.markdown(f"### Fig 4. Distribution des prix dans votre quartier en {self.selected_year}")
            self.plot_5()

    def plot_1(self):

        col1, col2 = st.columns(2)  # Créer deux colonnes

        with col2:
            mapbox_styles = ["open-street-map", "carto-positron", "carto-darkmatter", "white-bg"]
            default_map = mapbox_styles.index("open-street-map")
            self.selected_mapbox_style = st.selectbox("Style de carte", mapbox_styles, index=default_map)

            colormaps = ["Rainbow", "Portland", "Jet", "Viridis", "Plasma", "Cividis", "Inferno", "Magma", "RdBu"]
            default_cmap = colormaps.index("Jet")
            self.selected_colormap = st.selectbox("Echelle de couleurs", colormaps, index=default_cmap)

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
                                opacity=0.5, 
                                hover_data=['code_postal', 'valeur_fonciere', 'longitude', 'latitude'])
                        
        # Update the map style
        fig.update_layout(mapbox_style=self.selected_mapbox_style)
        fig.update_coloraxes(colorbar_thickness=10, colorbar_title_text="", colorbar_x=1, colorbar_xpad=0, colorbar_len=1.0, colorbar_y=0.5)
        fig.update_layout(height=800)

        st.plotly_chart(fig, use_container_width=True)

    def plot_2(self):
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

    def plot_3(self):

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
        fig = px.bar(grouped, x='Postal Code', y='Property Value')

        # Update the bar chart
        fig.update_traces(text=grouped['Count'], textposition='outside')
        fig.update_xaxes(type='category')
        fig.update_layout(height=600, yaxis_title='Prix médian en €', xaxis_title='Code postal')
        st.plotly_chart(fig, use_container_width=True)

    def plot_4(self):

        # Add a selectbox for choosing between bar and line plot
        plot_types = ["Bar", "Line"]
        self.selected_plot_type = st.selectbox("Selectionner une visualisation", plot_types, index=0)

        # Determine the column to display
        value_column = 'median_value_SQM' if self.normalize_by_area else 'median_value'

        # Filter the dataframe by the provided department code
        dept_data = self.summarized_df_pandas[self.summarized_df_pandas['code_postal'] == self.selected_department]
        dept_data.loc[:, 'type_local'] = dept_data['type_local'].apply(shorten_titles)

        # Generate a brighter linear color palette
        years = sorted(dept_data['Year'].unique())
        color_scale = cm.Blues(np.linspace(0.3, 1, len(years)))  # Using a brighter section of the viridis colormap
        color_scale_rgb = ["rgb({}, {}, {})".format(int(r*255), int(g*255), int(b*255)) for r, g, b, _ in color_scale]
        year_color_map = dict(zip(years, color_scale_rgb))

        if self.selected_plot_type == "Bar":
            fig = go.Figure()

            # Data for each year
            for year in years:
                year_data = dept_data[dept_data['Year'] == year]
                fig.add_trace(go.Bar(
                    x=year_data['type_local'],
                    y=year_data[value_column],
                    name=str(year),
                    marker_color=year_color_map[year]
                ))

            fig.update_layout(barmode='group')  # Ensure bars are grouped, not stacked

        else:
            # Line plot using plotly
            fig = px.line(dept_data, 
                        x='Year', 
                        y=value_column, 
                        color='type_local',
                        labels={"median_value": "Prix médian en €", "Year": "Année"},
                        markers=True,
                        height=600)

        # Update the layout of the plotly figure
        fig.update_layout(xaxis_title="Type de bien",
                yaxis_title="Prix médian en €",
                legend_title="Type de bien",
                height=600)
        fig.update_layout(legend_orientation="h", 
                        legend=dict(y=1.1, x=0.5, xanchor='center', title_text=''))
        
        st.plotly_chart(fig, use_container_width=True)

    def plot_5(self):

        unique_postcodes = self.df_pandas['code_postal'].unique()
                
        ### Set up the postal code selectbox and update button
        selected_postcode = st.selectbox("Code postal", sorted(unique_postcodes))

        if st.button(f"Actualiser la carte pour {selected_postcode}"):
            st.session_state.selected_postcode = selected_postcode
            st.session_state.selected_postcode_title = selected_postcode
            st.experimental_rerun()


        # Si le bouton est cliqué, mettez à jour la carte avec les données du code postal sélectionné
        filtered_by_postcode = self.df_pandas[self.df_pandas['code_postal'] == selected_postcode]
        filtered_by_postcode.loc[:, 'type_local'] = filtered_by_postcode['type_local'].apply(shorten_titles)

        unique_property_types = filtered_by_postcode['type_local'].unique()

        traces = []

        color_palette = sns.color_palette('tab10', len(unique_property_types)).as_hex()
        colors = dict(zip(unique_property_types, color_palette))

        for property_type in unique_property_types:
            subset = filtered_by_postcode[filtered_by_postcode['type_local'] == property_type]
            traces.append(go.Box(y=subset['valeur_fonciere'], 
                                name=property_type, 
                                marker_color=colors[property_type], 
                                boxpoints='all', 
                                jitter=0.3, 
                                pointpos=0, 
                                marker=dict(opacity=0.5)))
            
        fig = go.Figure(data=traces)
        fig.update_layout(xaxis_title='Type de bien', yaxis_title='Prix médian en €')
        fig.update_layout(height=600)
        fig.update_layout(legend_orientation="h", legend=dict(y=1.1, x=0.5, xanchor='center'))
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    PropertyApp()
