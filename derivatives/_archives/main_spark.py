import streamlit as st
from pyspark.sql import SparkSession
import requests
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import functions as F
from PIL import Image
import seaborn as sns

# source env/bin/activate

# info_message = '''This app was created by Ludovic Gardy, Sotis A.I, 2023. The information displayed is based on the French
#             open data portal (https://www.data.gouv.fr/fr/), where you can find more details about the data. This version 
#             of the app is a prototype, and the data is limited to the years 2018-2022. The app is not optimized for mobile
#             devices. A new version will be released in the future, with more features and a better user experience.
#             A streaming version of the app will come soon as well, with a Kafka cluster and a Spark Streaming job. Stay tuned!
#             If you have any questions, please contact me at ludovic.gardy@sotisanalytics.com. Enjoy!'''

spark = SparkSession.builder \
    .appName("Read CSV with PySpark") \
    .getOrCreate()

class PropertyApp:
    
    def __init__(self):
        st.set_page_config(layout="wide")

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
             If you have any questions, contact me at ludovic.gardy@sotisanalytics.com. Enjoy!'''
            st.info(info_message)

    def display_logo(self, logo_col):
        logo_path = "https://www.sotisanalytics.com/images/logos/Sotis_A-A.png"  
        response = requests.get(logo_path)
        img = Image.open(BytesIO(response.content))
        desired_width = 60
        logo_col.image(img, width=desired_width, caption='', output_format='PNG')

    def load_data_and_initialize_params(self):

        @st.cache_data
        def load_data(selected_dept, year):
            url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/{selected_dept}.csv.gz"
            response = requests.get(url)
            buffer = BytesIO(response.content)
            df_pandas = pd.read_csv(buffer, compression='gzip', header=0, sep=',', quotechar='"', low_memory=False, 
                                    usecols=["type_local", "valeur_fonciere", "code_postal", "surface_reelle_bati", "longitude", "latitude"])
            df_pandas.dropna(inplace=True)
            df_spark = spark.createDataFrame(df_pandas)
            df_spark = df_spark.withColumn("code_postal", F.format_string("%05d", df_spark["code_postal"].cast("int")))
            return df_spark.toPandas()

        st.title("Property Value by Postal Code for Each Property Type")

        departments = [str(i).zfill(2) for i in range(1, 101)]
        years = [str(y) for y in range(2018, 2023)]
        default_dept = departments.index("06")
        default_year = years.index("2022")
        self.selected_department = st.selectbox("Select a department", departments, index=default_dept)
        self.selected_year = st.selectbox("Select a year", years, index=default_year)
        self.df_spark = load_data(self.selected_department, self.selected_year)
        property_types = sorted(self.df_spark['type_local'].unique())
        selectbox_key = f"local_type_{self.selected_department}_{self.selected_year}"
        self.selected_property_type = st.selectbox("Select a property type", property_types, key=selectbox_key)

        mapbox_styles = ["open-street-map", "carto-positron", "carto-darkmatter", "white-bg"]
        colormaps = ["Viridis", "Plasma", "Cividis", "Inferno", "Magma", "RdBu"]
        default_map = mapbox_styles.index("open-street-map")
        default_cmap = colormaps.index("Inferno")
        self.selected_mapbox_style = st.selectbox("Select a map style", mapbox_styles, index=default_map)
        self.selected_colormap = st.selectbox("Select a colormap", colormaps, index=default_cmap)
        self.normalize_by_area = st.checkbox("Price per m²")
        if self.normalize_by_area:
            self.df_spark['valeur_fonciere'] = self.df_spark['valeur_fonciere'] / self.df_spark['surface_reelle_bati']



    def create_plots(self):
        self.plot_1()
        self.plot_2()
        self.plot_3()
        self.plot_4()

    def plot_1(self):
        st.title("Property Value by Postal Code for Each Property Type")

        fig = px.scatter_mapbox(self.df_spark, 
                                 lat='latitude', 
                                 lon='longitude', 
                                 color='valeur_fonciere', 
                                 size='valeur_fonciere', 
                                 color_continuous_scale=self.selected_colormap, 
                                 size_max=15, 
                                 zoom=6, 
                                 title="Price Distribution By Geographic Location")
        fig.update_layout(mapbox_style=self.selected_mapbox_style)
        fig.update_coloraxes(colorbar_thickness=10, colorbar_title_text="", colorbar_x=1, colorbar_xpad=0, colorbar_len=1.0, colorbar_y=0.5)
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

    def plot_2(self):
        filtered_df = self.df_spark[self.df_spark['type_local'] == self.selected_property_type]
        grouped = filtered_df.groupby('code_postal').agg({
            'valeur_fonciere': 'mean',
            'type_local': 'count'
        }).reset_index()
        grouped.columns = ['Postal Code', 'Property Value', 'Count']
        fig = px.bar(grouped, x='Postal Code', y='Property Value', 
                    title=f'Average Property Price by Postal Code for {self.selected_property_type} in {self.selected_year}')
        
        # Ajout d'un sous-titre au graphique
        fig.add_annotation(
            dict(
                x=0.5,  # x positionne le texte au centre
                y=1,  # y positionne le texte juste en dessous du titre
                showarrow=False,
                text="Numbers above bars represent count of properties per postal code. They provide context on the volume of sales for each postal area.",  # Texte du sous-titre
                xref="paper",
                yref="paper",
                font=dict(size=12, color="grey")  # Taille et couleur du sous-titre
            )
        )
        fig.update_traces(text=grouped['Count'], textposition='outside')
        fig.update_xaxes(type='category')
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    def plot_3(self):
        grouped_data = self.df_spark.groupby(["code_postal", "type_local"]).agg({
            "valeur_fonciere": "mean"
        }).reset_index()

        fig = px.line(grouped_data, x='code_postal', y='valeur_fonciere', color='type_local', 
                    title='Average Price for Different Property Types Based on Postal Code', 
                    markers=True, labels={'valeur_fonciere': 'Average Price', 'code_postal': 'Postal Code'})

        fig.update_xaxes(type='category', tickvals=grouped_data["code_postal"].unique(), range=[-0.5, len(grouped_data["code_postal"].unique()) - 0.5], title_text='Postal Code')
        fig.update_yaxes(title_text='Average Price')
        fig.update_layout(legend_orientation="h", legend=dict(y=1.1, x=0.5, xanchor='center'))
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    def plot_4(self):
        st.title("Property Value Details for a Specific Postal Code")

        unique_postcodes = self.df_spark['code_postal'].unique()
        selected_postcode = st.selectbox("Select a postal code", sorted(unique_postcodes))

        filtered_by_postcode = self.df_spark[self.df_spark['code_postal'] == selected_postcode]

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
    # PropertyApp(spark)
    PropertyApp()
