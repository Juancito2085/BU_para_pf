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
    "g_metadata": [
        bigquery.SchemaField("gmap_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("zip_code", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("latitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("longitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("category", "STRING", mode="NULLABLE")
    ],
    "g_reviews": [
        bigquery.SchemaField("gmap_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("rating", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("time", "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("review", "STRING", mode="NULLABLE")
    ],
    "y_checkin": [
        bigquery.SchemaField("business_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("date", "DATETIME", mode="NULLABLE")
    ],
    "y_business": [
        bigquery.SchemaField("business_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("state", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("postal_code", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("latitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("longitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("stars", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("review_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("is_open", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("categories", "STRING", mode="NULLABLE")
    ],
    "y_reviews": [
        bigquery.SchemaField("review_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("business_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("stars", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("useful", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("text", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("date", "DATETIME", mode="NULLABLE")
    ],
    "y_users": [
        bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("review_count", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("useful", "INTEGER", mode="NULLABLE")
    ]
}

# Utiliza la función para crear el dataset y las tablas
bq_create_dataset("proyecto-final-427203", "YELP_GMAPS", tablas)



