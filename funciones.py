import pandas as pd
from textblob import TextBlob
import re
from math import radians, sin, cos, sqrt, atan2

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
            if len(lista) >= 11:
                break
            if row.iloc[1] == i:
                lista.append(j)
            else:
                lista.append(-1)
        if len(lista) >= 11:
            break
    return lista[:11] 