import streamlit as st
import  bz2
import joblib
import pandas as pd
from funciones import plot_predictions_for_categories
from funciones import plot_predictions_for_city
import matplotlib.pyplot as plt
import pickle
import datetime
import calendar
import torch
import gcsfs
from io import BytesIO
import requests
from streamlit_folium import folium_static

df_full = pd.read_parquet(r'ML_streamlit/Datos/ML_1.parquet')
df_categorias = pd.read_parquet(r'ML_streamlit/Datos/categorias_numeros.parquet')
df_ciudades = pd.read_parquet(r'ML_streamlit/Datos/ciudad_numeros.parquet')
df_full_2 = pd.read_parquet(r'ML_streamlit/Datos/df_modelo.parquet')

# Lee el contenido del archivo styles.css y aplica el estilo
with open("ML_streamlit/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Muestra la imagen usando una ruta relativa
st.image("ML_streamlit/Logo.jpeg", use_column_width=True)
st.markdown("""
    
    <div class="header">
        <h1>Proyecto Google-YELP</h1>
    </div>
    <div class="content">
        <!-- Contenido principal de la presentación -->
        <p>Aquí va el contenido principal de la presentación.</p>

    </div>
""", unsafe_allow_html=True)







#Abrimos el modelo
@st.cache(allow_output_mutation=True)
def abrir_modelo(bucket_name, file_name):
    url="https://storage.googleapis.com/modelo_ml_111/Segementacion_modelo_bz2.pkl.bz2"

    response=requests.get(url)
    # Asegúrate de que la solicitud fue exitosa
    if response.status_code == 200:
        # Crea un stream de bytes a partir del contenido comprimido
        compressed_content = BytesIO(response.content)
        
        # Descomprime y carga el modelo directamente desde el stream de bytes
        with bz2.open(compressed_content, 'rb') as f:
            clf = joblib.load(f)
        
        return clf
    else:
        raise Exception(f"Error al acceder al archivo: {response.status_code}")

# Ejemplo de uso
bucket_name = 'modelo_ml_111'
file_name = 'Segementacion_modelo_bz2.pkl.bz2'
clf = abrir_modelo(bucket_name, file_name) 



modelo_seleccionado=st.sidebar.selectbox("Seleccione el tipo de modelo: ", ["Predicción de crecimiento", "Identificación de oportunidades"])


def entrada_seleccionada(modelo):
    if modelo=="Predicción de crecimiento":
        categorias=df_categorias['category'].unique()
        categorias=sorted(categorias)
        categoria_seleccionada = st.sidebar.selectbox("Seleccione las categorías:", categorias)
        categoria_seleccionada=[categoria_seleccionada]
        return categoria_seleccionada, 0
    else:
        ciudades=df_ciudades['city'].unique()
        ciudades=sorted(ciudades)
        ciudad_seleccionada = st.sidebar.selectbox("Seleccione una ciudad:", ciudades)
        cantidad=st.sidebar.slider("Seleccione la cantidad de categoris", 1, 5, 1)
        ciudad_seleccionada=ciudad_seleccionada
        return ciudad_seleccionada, cantidad

entrada, cantidad=entrada_seleccionada(modelo_seleccionado)

#Creamos las columnas
col1, col2 = st.columns(2)

if modelo_seleccionado=="Predicción de crecimiento":
    img, mapa = plot_predictions_for_categories(entrada,clf)
    with col1:
        imagen=st.image(img, caption='Gráfico de Predicciones por Ciudad', use_column_width=True)
    with col2:
        mapa_terminado=folium_static(mapa)
else:
    img, mapa = plot_predictions_for_city(entrada,clf,cantidad)
    imagen=st.image(img, caption='Gráfico de Predicciones por Categoría')
    mapa_terminado=folium_static(mapa)