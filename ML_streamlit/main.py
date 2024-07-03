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
st.title("Proyecto Google-YELP")



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


if modelo_seleccionado=="Predicción de crecimiento":
    img, mapa = plot_predictions_for_categories(entrada,clf)
    st.image(img, caption='Gráfico de Predicciones por Ciudad', use_column_width=True)
    folium_static(mapa)
else:
    img, mapa = plot_predictions_for_city(entrada,clf,cantidad)
    st.image(img, caption='Gráfico de Predicciones por Categoría' ,use_column_width=True)
    folium_static(mapa)