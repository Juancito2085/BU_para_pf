

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

    #Nos quedamos con los restaurantes de los estados de Florida, Texas, California, New York y Pennsylvania
    df = df[df['state'].isin(['FL', 'TX', 'CA', 'NY', 'PA'])]
    
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

#Transformaciones de business
def transform_business(df):

    #Nos quedamos con las columnas que nos interesan
    df=df.iloc[:,:14]

    #Eliminamos las columnas que no nos interesan
    df.drop(columns=['attributes'], inplace=True)

    #Eliminamos las filas de la columna 'categories' donde hay nulos
    df.dropna(subset=['categories'], inplace=True)

    #Definimos las palabras claves
    palabras_claves = ['restaurant', 'food','steakhouse','mexican','pizzeria','american','asian']

    #Realizamos una función para convertir un string en una lista de palabras
    def string_to_list(x):
        return [item.strip() for item in x.split(',')]
    
    #Realizamos una función para filtrar las palabras claves
    def filter_list_by_keywords(lst, palabras_claves):
        return [word for word in lst if any(palabra.lower() in word.lower() for palabra in palabras_claves)]
    
    #Convertimos la columna 'categories' en una lista
    df['categories'] = df['categories'].apply(string_to_list)

    #Filtramos las palabras claves
    df['categories'] = df['categories'].apply(lambda x: filter_list_by_keywords(x, palabras_claves))

    #Realizamos una funcion para extraer las palabras claves que no tengan que ver con el rubro
    def filter_list_by_keywords(lst, palabras_claves):
        return [word for word in lst if any(palabra.lower() in word.lower() for palabra in palabras_claves)]
    
    #Eliminamos las filas con listas vacias
    df = df[df['categories'].apply(lambda x: len(x) > 0)]

    #Reseteamos el index
    df.reset_index(drop=True, inplace=True)

    #Limpiamos los strings 
    df['name'] = df['name'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df['address'] = df['address'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df['city'] = df['city'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df['state'] = df['state'].apply(lambda x: x.strip() if isinstance(x, str) else x)

    #Creamos una funcion para verificar la ciudad y el estado
    def get_location(row):
        coordinates = [(row['latitude'], row['longitude'])]
        location = reverse_geocode.search(coordinates)[0]
        if location['country_code'] == 'US':
            return pd.Series([location['city'], location['state']])
        else:
            return pd.Series([None, None])

    df[['city', 'state']] = df.apply(get_location, axis=1)

    #Cambiamos los nombres de los estados por sus abreviaturas de los estados que nos interesan
    df['state'] = df['state'].map({'Florida':'FL','Texas':'TX','California':'CA','New York':'NY','Pennsylvania':'PA'})

    #Filtramos los restaurantes por estado
    lista_estados=['FL','TX','CA','NY','PA']
    df = df[df['state'].isin(lista_estados)]

    #Se cambian los tipos de datos de latitude, logitude,stars,review_count
    df = df.astype({
        'latitude': 'float64',
        'longitude': 'float64',
        'stars': 'float32',
        'review_count': 'int64'
    })

    #Borramos la columna hours que finalmente no se usará
    df.drop(columns=['hours'], inplace=True)

    return df
#Trastransformaciones de chekin
def transform_checkin(df):
    
    #Convertimos la cadena de texto a lista
    df['date'] = df['date'].str.split(',')

    # Usamos explode
    df = df.explode('date')

    #Normalizamos la columna date
    df['date'] = df['date'].astype(str)
    df['date'] = df['date'].str.strip()
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    #Nos quedamos con los datos que estan entre 2016 y 2021
    df = df[(df['date'].dt.year >= 2016) & (df['date'].dt.year <= 2021)]

    return df

#Transformaciones de user
def transform_user(df):

    #Nos quedamos con las columnas que nos interesan
    df=df[['user_id','name','review_count','useful']]

    #Eliminamos las filas duplicadas
    df=df.drop_duplicates(keep='first')

    return df
