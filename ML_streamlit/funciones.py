import pandas as pd
from textblob import TextBlob
import re
from math import radians, sin, cos, sqrt, atan2
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import io

def sentiment_score(review:str) -> int:
  
    if not review:
        return 1
    else:
        analisis = TextBlob(review)
        if analisis.sentiment.polarity < -0.2:
            return 0  
        elif analisis.sentiment.polarity > 0.2:
            return 2  
        else:
            return 1  
        
def separar_fecha(cadena: str) -> tuple:
    find = re.search(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', str(cadena))
    if find:
        return find.group(1), find.group(2), find.group(3), find.group(4), find.group(5), find.group(6)
    else:
        return None, None, None, None, None, None
    
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    r = 6371
    return c * r

def ciudad_numero_funcion(ciudad, df):
    for i, row in df.iterrows():
        if row.iloc[1] == ciudad:
            return i
    return -1

def lat_lon(ciudad, df):
    if ciudad in df['city'].values:
        lat=df[df['city']==ciudad]['latitude'].values[0]
        lon=df[df['city']==ciudad]['longitude'].values[0]
        return lat, lon
    else:
        return None, None
    
def categorias_funcion(categoria,df):
    lista = []
    for i in categoria:
        for j, row in df.iterrows():
            if len(lista) >= 5:
                break
            if row.iloc[1] == i:
                lista.append(j)
            else:
                lista.append(-1)
        if len(lista) >= 5:
            break
    return lista[:5] 

def plot_predictions_for_categories(categorias1, df_full, df_ciudades, df_full_2, df_categorias, model):
    ciudades_unicas = set(df_full['city'].values)
    predicciones = []
    fechas = []
    ciudades = []
    for ciudad in ciudades_unicas:
        ciudad_numero = ciudad_numero_funcion(ciudad, df_ciudades)
        lat, lon = lat_lon(ciudad_numero, df_full_2)
        categoria_numeros = categorias_funcion(categorias1, df_categorias)
        for anio in [2019]:
            for mes in range(1, 13):
                features = [ciudad_numero, lat, lon] + categoria_numeros + [anio, mes]
                columns = ['city', 'latitude', 'longitude', 'category_1', 'category_2', 'category_3', 
                           'category_4', 'category_5', 'year', 'month']
                features_df = pd.DataFrame([features], columns=columns)
                prediccion = model.predict(features_df)[0]
                predicciones.append(prediccion)
                fechas.append(f"{anio}-{mes:02d}")
                ciudades.append(ciudad)
    resultados_df = pd.DataFrame({'city': ciudades, 'fecha': fechas, 'predicciones': predicciones,'latitud':lat,'longitud':lon})
    resultados_df['fecha'] = pd.to_datetime(resultados_df['fecha'])
    scaler = MinMaxScaler()
    resultados_df['predicciones'] = scaler.fit_transform(resultados_df[['predicciones']])
    condicion_prediccion = resultados_df['predicciones'].mean() + 1.8 * resultados_df['predicciones'].std()
    ciudades_filtradas = resultados_df.groupby('city').filter(lambda x: x['predicciones'].mean() > condicion_prediccion)
    categoria_string = ' - '.join(categorias1)
    return ciudades_filtradas
    '''plt.figure(figsize=(12, 8))
    for ciudad in ciudades_filtradas['city'].unique():
        ciudad_df = ciudades_filtradas[ciudades_filtradas['city'] == ciudad]
        plt.plot(ciudad_df['fecha'], ciudad_df['predicciones'], label=ciudad)
    plt.xlabel('Fecha')
    plt.ylabel('Predicciones')
    plt.title(f'Predicciones por ciudad de la categoría {categoria_string}')
    plt.legend(title='Ciudad', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.subplots_adjust(left=0.1, right=0.75, top=0.9, bottom=0.2)
    
    plt.show()'''
#coordenadas=lat_lon(lat, lon)
def lat_long(latitud,longitud):
    return (latitud,longitud)


def plot_predictions_for_city(df_categorias, df_ciudad, df_full_2, model, ciudad):
    predicciones = []
    fechas = []
    categorias_unicas = []
    for categoria_1 in df_categorias['category']:
        for categoria_2 in df_categorias['category']:
            if categoria_1 != categoria_2:
                categorias = [categoria_1, categoria_2]
                ciudad_numero = ciudad_numero_funcion(ciudad, df_ciudad)
                lat, lon = lat_lon(ciudad_numero, df_full_2)
                categoria_numeros = categorias_funcion(categorias, df_categorias)
                for anio in [2019]:
                    for mes in range(1, 13):
                        features = [ciudad_numero, lat, lon] + categoria_numeros + [anio, mes]
                        columns = ['city', 'latitude', 'longitude', 'category_1', 'category_2', 'category_3', 
                                   'category_4', 'category_5', 'year', 'month']
                        features_df = pd.DataFrame([features], columns=columns)
                        prediccion = model.predict(features_df)[0]
                        predicciones.append(prediccion)
                        fechas.append(f"{anio}-{mes:02d}")
                        categorias_unicas.append(categorias)
            else:
                continue
    resultados_df = pd.DataFrame({'categorias': categorias_unicas, 'fecha': fechas, 'predicciones': predicciones})
    resultados_df['fecha'] = pd.to_datetime(resultados_df['fecha'])
    scaler = MinMaxScaler()
    resultados_df['predicciones'] = scaler.fit_transform(resultados_df[['predicciones']])
    condicion_prediccion_2 = resultados_df['predicciones'].mean() + 0.1 * resultados_df['predicciones'].std()
    resultados_df['categorias'] = resultados_df['categorias'].apply(lambda x: ' - '.join(x) if isinstance(x, list) else x)
    categorias_filtradas = resultados_df.groupby('categorias').filter(lambda x: x['predicciones'].mean() > condicion_prediccion_2)
    plt.figure(figsize=(12, 8))
    for categoria in categorias_filtradas['categorias'].unique():
        categoria_df = categorias_filtradas[categorias_filtradas['categorias'] == categoria]
        plt.plot(categoria_df['fecha'], categoria_df['predicciones'], label=categoria)
    plt.xlabel('Fecha')
    plt.ylabel('Predicciones')
    plt.title(f'Predicciones por categoria en la ciudad {ciudad}')
    plt.legend(title='Categorias', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.subplots_adjust(left=0.1, right=0.75, top=0.9, bottom=0.2)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return img