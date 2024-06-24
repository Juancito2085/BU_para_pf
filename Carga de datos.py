
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Sube un archivo al bucket."""
    # El ID del bucket
    # El path al archivo a subir
    # El ID del blob

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"Archivo {source_file_name} subido a {destination_blob_name}."
    )

# Ejemplo de uso
upload_blob('tu-bucket', 'local/path/a/tu/archivo', 'destino/en/bucket')