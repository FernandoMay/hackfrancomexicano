import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

st.set_page_config(page_title="Ecobici CDMX – Clasificación de Estaciones", layout="wide")

st.title("🚲 Clasificación de Estaciones Ecobici CDMX")

# --- Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data/estaciones.csv")
    gdf_zones = gpd.read_file("data/cdmx_zones.geojson")
    return df, gdf_zones

df, gdf_zones = load_data()

# --- Formato largo para animación por día
dias = {
    "Monday": "lunt", "Tuesday": "mart", "Wednesday": "miet",
    "Thursday": "juet", "Friday": "viet", "Saturday": "sabt", "Sunday": "domt"
}
df_long = pd.concat([
    df[['idestacion', 'lat', 'lon']].assign(tipoestacion=df[col], day=day)
    for day, col in dias.items()
], ignore_index=True)

color_map = {
    1: 'lightblue', 2: 'orange', 3: 'orange',
    4: 'yellow', 5: 'yellow', 6: 'green'
}
df_long['color'] = df_long['tipoestacion'].map(color_map)

# --- Modo de visualización
modo = st.radio("Selecciona una visualización:", ["🌀 Comparador animado por día", "📊 Histograma por alcaldía"])

if modo.startswith("🌀"):
    st.subheader("🌀 Animación por Día de la Semana")

    fig_anim = px.scatter_mapbox(
        df_long,
        lat="lat",
        lon="lon",
        animation_frame="day",
        color="color",
        hover_name="idestacion",
        zoom=11,
        height=600,
        mapbox_style="carto-positron",
        color_discrete_map="identity",
        title="Evolución del Tipo de Estación por Día – CDMX"
    )
    st.plotly_chart(fig_anim, use_container_width=True)

elif modo.startswith("📊"):
    st.subheader("📊 Histograma por Alcaldía")

    # GeoDataFrame con puntos de estaciones
    gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")

    # Unión espacial con zonas
    gdf_joined = gpd.sjoin(gdf_points, gdf_zones, how="inner", predicate="intersects")

    # Agrupar por alcaldía y tipo
    conteo = gdf_joined.groupby(['mun_name', 'tipoestacion']).size().reset_index(name="count")

    # Texto descriptivo
    st.markdown("Este gráfico muestra cuántas estaciones de cada tipo (1-6) existen en cada alcaldía de CDMX.")

    fig_bar = px.bar(
        conteo,
        x="mun_name",
        y="count",
        color="tipoestacion",
        barmode="stack",
        title="Estaciones por Tipo y Alcaldía",
        labels={"mun_name": "Alcaldía", "count": "Número de Estaciones", "tipoestacion": "Tipo"}
    )
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)
