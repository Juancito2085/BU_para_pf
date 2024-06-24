from google.cloud import bigquery
from google.oauth2 import service_account

# Carga las credenciales de la cuenta de servicio
credentials_path = 'proyecto-final-427203-46b55ede3af3.json'
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Función para crear un dataset y tablas en BigQuery
def bq_create_dataset(project_id, dataset_name, tablas):
    # Inicializa el cliente de BigQuery con las credenciales cargadas
    client = bigquery.Client(credentials=credentials, project=project_id)

    # Construye el identificador completo del dataset
    dataset_id = f"{project_id}.{dataset_name}"

    # Crea un objeto Dataset
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"

    # Crea el dataset en BigQuery
    dataset = client.create_dataset(dataset, timeout=30)  # Llamada a la API
    print(f"Dataset creado {dataset.project}.{dataset.dataset_id}")

    # Itera sobre la lista de tablas y crea cada una
    for table_name, schema in tablas.items():
        table_id = f"{dataset_id}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)  # Llamada a la API
        print(f"Tabla creada {table_id}")

# Definición de las tablas a crear
tablas = {
    "metadata": [
        bigquery.SchemaField("gmap_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("address", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("city", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("state", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("zip_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("latitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("longitude", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED")
    ],
    "reviews": [
        bigquery.SchemaField("gmap_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("rating", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("review", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED")
    ]
}

# Utiliza la función para crear el dataset y las tablas
bq_create_dataset("proyecto-final-427203", "YELP_GMAPS", tablas)

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

#Transformaciones de review

def transform_user(df):

    #Nos quedamos con las columnas que nos interesan
    df=df[['user_id','name','review_count','useful']]

    #Eliminamos las filas duplicadas
    df=df.drop_duplicates(keep='first')

    return df