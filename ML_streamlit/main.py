import streamlit as st
import  bz2
import joblib
import pandas as pd
from funciones import *
import matplotlib.pyplot as plt
import pickle
import datetime
import calendar


df_full = pd.read_parquet(r'\Datos\ML_1.parquet')
df_categorias = pd.read_parquet(r'Datos\categorias_numeros.parquet')
df_ciudades = pd.read_parquet(r'Datos\ciudad_numeros.parquet')
df_full_2 = pd.read_parquet(r'Datos\df_modelo.parquet')
st.title("Proyecto Google-YELP")

modelo_seleccionado=st.sidebar.selectbox("Seleccione el tipo de modelo: ", ["Predicción de crecimiento", "Identificación de oportunidades"])



def entrada_seleccionada(modelo):
    if modelo=="Predicción de crecimiento":
        categorias=['Fast Food', 'Italian', 'East Asian', 'Mexican', 'American','Chinese', 'Veggie Vegan', 'Caribbean',
                     'Latin American', 'Middle East', 'Indian', 'Spanish', 'French', 'Greek', 'Jew','African']
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

#Abrimos el modelo

with bz2.BZ2File ('Datos\Segementacion_modelo_float16.pkl', 'rb') as f:
    clf = joblib.load(f)

def predict_2(categoria):
    img = plot_predictions_for_categories(categoria, df_full, df_ciudades, df_full_2, df_categorias, clf)
    return img

'''def predict(city):
    img = plot_predictions_for_city(df_categorias, df_ciudades, df_full_2, model, city)
    return send_file(img, mimetype='image/png')'''


ciudades_filtradas=predict_2(categoria_seleccionada)
st.write(ciudades_filtradas.columns)
st.write(ciudades_filtradas[['latitud','longitud']].iloc[:5])
#plot del primer modelo
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

st.pyplot(fig1)