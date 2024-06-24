

#Transformaciones para metadata
def transform_metadata(df):
    #Eliminamos columnas que no nos interesan
    df.drop(columns=['index','description','hours','MISC','relative_results','url','price'],inplace=True)
    #Eliminamos filas con valores nulos en la columna category
    df.dropna(subset='category',inplace=True)
    #Filtramos el dataset con las palabras claves
    palabras_claves = ['restaurant', 'food','steakhouse','mexican','pizzeria','american','asian']
    #Expando categoría

    #Genero una función para filtrar las palabras claves
    def filter_list_by_keywords(lst, palabras_claves):
        return [word for word in lst if any(palabra.lower() in word.lower() for palabra in palabras_claves)]
    
    #Aplico la función a la columna category
    df['category'] =df['category'].apply(lambda x: filter_list_by_keywords(x, palabras_claves))

    #Nos quedamos con las filas que no tienen nulos en la columna category
    df = df[df['category'].apply(lambda x: len(x) > 0)]

    #Reseteamos el índice
    df.reset_index(drop=True, inplace=True)

    #Eliminamos los restaurantes que están permanentemente cerrados
    df=df[df['state']!='Permanently closed']

    #Eliminamos la columna state
    df.drop(columns='state',inplace=True)

    #Eliminamos las filas que tengan el mismo gmap_id
    df.drop_duplicates(subset='gmap_id',inplace=True)

    #Vamos a extraer la ciudad y el código postal de la columna address
    df['city'] =df['address'].str.extract(r',\s*([^,]+),\s*[A-Z]{2}\s+\d{5}', expand=False)
    df['zip_code'] =df['address'].str.extract(r'(\d{5})$', expand=False)

    #Creamos una funcion para verificar la ciudad y el estado
    def get_location(row):
        coordinates = [(row['latitude'], row['longitude'])]
        location = reverse_geocode.search(coordinates)[0]
        if location['country_code'] == 'US':
            return pd.Series([location['city'], location['state']])
        else:
            return pd.Series([None, None])

    df[['city', 'estado']] = df.apply(get_location, axis=1)

    #Completo los nulos con "Sin Datos"
    df.fillna('Sin Datos', inplace=True)

    #Renombramos las columnas correspondientes
    df.rename(columns={'estado':'state'},inplace=True)

    #Reordenamos las columnas
    df =df[['gmap_id', 'name', 'address', 'city', 'state', 'zip_code', 'latitude', 'longitude', 'category']]

    def abreviacion_estado(row):
        if row['state'] == 'New York':
            return 'NY'
        elif row['state'] == 'California':
            return 'CA'
        elif row['state'] == 'Texas':
            return 'TX'
        elif row['state'] == 'Florida':
            return 'FL'
        elif row['state'] == 'Pennsylvania':
            return 'PA'
        else:
            return 'Sin Datos'

    df['state'] = df.apply(abreviacion_estado, axis=1)
    
    #Finalmente devolvemos el dataframe
    return df

#Transformaciones para reviews	
def transform_reviews(df):
    
    #Eliminamos las columnas que no nos interesan
    df.drop(columns=['pics','resp'],inplace=True)

    #Reordenamos las columnas 
    df=df[['gmap_id','name','rating','time','text']]

    #Modificamos la columna time para tener fecha
    df['time']=pd.to_datetime(df['time'], unit='ms')

    #Nos quedamos con las reviews de los años 2016 a 2021
    df=df[(df['time'].dt.year>=2016) & (df['time'].dt.year<=2021)]
    return df
