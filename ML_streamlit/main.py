import streamlit as st
import  bz2
import joblib
import pandas as pd
from funciones import plot_predictions_for_categories
import matplotlib.pyplot as plt
import pickle
import datetime
import calendar
import torch
import gcsfs
from io import BytesIO
import requests



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
        return categoria_seleccionada
    else:
        ciudades=['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego',
                 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco']
        ciudades=sorted(ciudades)
        ciudad_seleccionada = st.sidebar.selectbox("Seleccione una ciudad:", ciudades)
        return ciudad_seleccionada

categoria_seleccionada=entrada_seleccionada(modelo_seleccionado)

def predict_2(categoria,clf):
    img = plot_predictions_for_categories(categoria,clf)
    return img


ciudades_filtradas=predict_2(categoria_seleccionada,clf)

'''#plot del primer modelo
fig1=plt.figure(figsize=(12, 8))
for ciudad in ciudades_filtradas['city'].unique():
    ciudad_df = ciudades_filtradas[ciudades_filtradas['city'] == ciudad]
    plt.plot(ciudad_df['fecha'].dt.month, ciudad_df['predicciones'], label=ciudad)
plt.xlabel('Fecha')
plt.ylabel('Predicciones')
plt.title(f'Predicciones por ciudad de la categoría {categoria_seleccionada}')
plt.legend(title='Ciudad', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.xticks(rotation=45)
plt.subplots_adjust(left=0.1, right=0.75, top=0.9, bottom=0.2) 
plt.show()

st.pyplot(fig1)'''