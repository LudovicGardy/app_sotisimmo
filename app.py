import streamlit as st
import requests
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import seaborn as sns
import numpy as np

# from pyspark.sql import SparkSession
# from pyspark.sql import functions as F
# import os

# source env/bin/activate

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

        with st.sidebar:
            self.create_toolbar()
            self.load_data_and_initialize_params()

        self.create_plots()

    def create_toolbar(self):
        logo_path = "https://www.sotisanalytics.com/images/logos/Sotis_A-A.png"  
        response = requests.get(logo_path)
        img = Image.open(BytesIO(response.content))
        desired_width = 60
        st.sidebar.image(img, width=desired_width, caption='', output_format='PNG')

        btn_info = st.sidebar.button("About this app.")

        if btn_info:
            st.session_state.show_info = not st.session_state.get('show_info', False)
        if st.session_state.get('show_info', False):
            info_message = '''This app was created by Ludovic Gardy, Sotis A.I, 2023. The information displayed is based on the French
             open data portal, where you can find more details about the data. This version 
             of the app is a prototype, not optimiszed for mobile devices, and the data is limited to the years 2018-2022. A new version 
             will be released in the future, with more features and a better user experience.
             A streaming version of the app will come soon as well, with a Kafka cluster and a Spark Streaming job.
             If you have any questions, contact me at contact@sotisanalytics.com. Enjoy!'''
            st.info(info_message)

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
        self.selected_department = st.selectbox("Select a department", departments, index=default_dept)

        ### Set up the year selectbox
        years = [str(y) for y in range(2018, 2023)]
        default_year = years.index("2022")
        self.selected_year = st.selectbox("Select a year", years, index=default_year)

        ### Load data
        self.df_pandas = load_data(self.selected_department, self.selected_year).copy()

        ### Set up the property type selectbox
        property_types = sorted(self.df_pandas['type_local'].unique())
        selectbox_key = f"local_type_{self.selected_department}_{self.selected_year}"
        self.selected_property_type = st.selectbox("Select a property type", property_types, key=selectbox_key)

        ### Set up the normalization checkbox
        self.normalize_by_area = st.checkbox("Price per m²")
        
        if self.normalize_by_area:
            self.df_pandas['valeur_fonciere'] = self.df_pandas['valeur_fonciere'] / self.df_pandas['surface_reelle_bati']

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
        st.title("Sotis A.I. Immobilier")
        st.header("A simple app to visualize real estate data in France")
        st.write("""
        The charts below depict the property values of real estate assets in France, 
        based on their geographical location and the type of property (house, apartment, etc.).
        Initially, the results are presented in a comprehensive manner. Subsequently, you can delve into the details 
        for a specific geographical area of interest. The sidebar offers a user-friendly interface 
        for easily configuring the application settings.
        """)

        st.header(f"Price distribution for {self.selected_property_type}")

        ### Set up the map style and colormap selectboxes
        col1, col2 = st.columns(2)  # Créer deux colonnes

        with col1:
            mapbox_styles = ["open-street-map", "carto-positron", "carto-darkmatter", "white-bg"]
            default_map = mapbox_styles.index("open-street-map")
            self.selected_mapbox_style = st.selectbox("Select a map style", mapbox_styles, index=default_map)
        with col2:
            colormaps = ["Rainbow", "Portland", "Jet", "Viridis", "Plasma", "Cividis", "Inferno", "Magma", "RdBu"]
            default_cmap = colormaps.index("Jet")
            self.selected_colormap = st.selectbox("Select a colormap", colormaps, index=default_cmap)

        col1, col2 = st.columns(2)
        with col1:
            self.use_fixed_marker_size = st.checkbox("Fixed marker size", False)
        with col2:
            self.use_jitter = st.checkbox("Jitter", True)
            self.jitter_value = 0.001


        self.plot_1()


        st.header("Median price by Property Type & Postal Code")
        self.plot_2()

        st.header(f"Median Property Price by Postal Code for {self.selected_property_type} in {self.selected_year}")
        st.write("""Numbers above bars represent count of properties per postal code. 
                 They provide context on the volume of sales for each postal area.""")

        self.plot_3()

        # Set the title of the section
        st.header("Explore in more details your area of interest")
        self.plot_4()

    def plot_1(self):
        
        # Filtring the dataframe by property type
        filtered_df = self.df_pandas[self.df_pandas['type_local'] == self.selected_property_type]
        
        # Further filtering if a postcode is selected
        if hasattr(st.session_state, 'selected_postcode'):
            filtered_df = filtered_df[filtered_df['code_postal'] == st.session_state.selected_postcode]

        # (Optional) Jittering : add a small random value to the coordinates to avoid overlapping markers
        #jitter = 0.001 # adjust this value according to the density of your data
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
                                size=size_column,  # utilisez la colonne 'marker_size' pour définir la taille des marqueurs
                                color_continuous_scale=self.selected_colormap, 
                                size_max=15,  # ajustez la taille maximale des marqueurs ici
                                zoom=6, 
                                opacity=0.5,  # ajustez l'opacité ici
                                title=f"Price distribution for {self.selected_property_type}")       
                        
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
        fig.update_xaxes(tickvals=tickvals, ticktext=ticktext, range=[tickvals[0], tickvals[-1]])
        fig.update_yaxes(title_text='Average Price')
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

        # Add a subtitle to the bar chart
        fig.add_annotation(
            dict(
                x=0.5,  # x positionne le texte au centre
                y=1,  # y positionne le texte juste en dessous du titre
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(size=12, color="grey")  # Taille et couleur du sous-titre
            )
        )

        # Update the bar chart
        fig.update_traces(text=grouped['Count'], textposition='outside')
        fig.update_xaxes(type='category')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    def plot_4(self):

        unique_postcodes = self.df_pandas['code_postal'].unique()
                
        ### Set up the postal code selectbox and update button
        selected_postcode = st.selectbox("Select a postal code to update map", sorted(unique_postcodes))

        if st.button("Update map"):
            st.session_state.selected_postcode = selected_postcode
            st.experimental_rerun()

        # Si le bouton est cliqué, mettez à jour la carte avec les données du code postal sélectionné
        filtered_by_postcode = self.df_pandas[self.df_pandas['code_postal'] == selected_postcode]

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
        fig.update_layout(title=f'Property Value Details for Postal Code {selected_postcode}', 
                        xaxis_title='Property Type', yaxis_title='Property Value')
        fig.update_layout(height=600)
        fig.update_layout(legend_orientation="h", legend=dict(y=1.1, x=0.5, xanchor='center'))
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 8501))
    PropertyApp()
